"""CLI function for a vehicle."""

import re
from typing import Any
from typing import cast

import aiohttp
import click
from tabulate import tabulate

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle
from renault_api.kamereon.helpers import DAYS_OF_WEEK
from renault_api.kamereon.models import ChargeDaySchedule
from renault_api.kamereon.models import ChargeSchedule
from renault_api.kamereon.models import KamereonVehicleChargingSettingsData
from renault_api.kamereon.schemas import KamereonVehicleChargingSettingsDataSchema
from renault_api.renault_vehicle import RenaultVehicle

_DAY_SCHEDULE_REGEX = re.compile(
    "(?P<prefix>T?)"
    "(?P<hours>[0-2][0-9])"
    ":"
    "(?P<minutes>[0-5][0-9])"
    "(?P<suffix>Z?)"
    ","
    "(?P<duration>[0-9]+)"
)
_HOURS_PER_DAY = 24


@click.group()
def schedule() -> None:
    """Display or update charge schedules."""
    pass


@schedule.command()
@click.pass_obj
@helpers.coro_with_websession
async def show(
    ctx_data: dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Display charge schedules."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    full_endpoint = await vehicle.get_full_endpoint("charge-schedule")
    response = await vehicle.http_get(full_endpoint)
    if "data" in response.raw_data and "attributes" in response.raw_data["data"]:
        _show_basic(response.raw_data["data"]["attributes"])
    else:
        _show_alternate(response.raw_data)


def _show_basic(response: dict[str, Any]) -> None:
    """Display charge schedules (basic)."""
    calendar = response["calendar"]
    schedule_table: list[list[str]] = []
    for day in DAYS_OF_WEEK:
        day_data = calendar[day][0]
        start_time = day_data["startTime"]
        end_time = str(
            int(day_data["startTime"])
            + int(day_data["duration"] * 100 / 60)
            + (day_data["duration"] % 60)
        )
        schedule_table.append(
            [
                day.capitalize(),
                helpers.get_display_value(
                    f"T{start_time[0:2]}:{start_time[2:4]}Z", "tztime"
                ),
                helpers.get_display_value(
                    f"T{end_time[0:2]}:{end_time[2:4]}Z", "tztime"
                ),
                day_data["duration"],
                day_data["activationState"],
            ]
        )

    headers = ["Day", "Start time", "End time", "Duration", "Active"]
    click.echo(tabulate(schedule_table, headers=headers))


def _show_alternate(response: dict[str, Any]) -> None:
    """Display charge schedules (alternate)."""
    click.echo(f"Mode: {response['chargeModeRq'].capitalize()}")
    if not response["programs"]:
        click.echo("\nNo schedules found.")
        return

    for idx, program in enumerate(response["programs"]):
        active = " [Active]" if program["programActivationStatus"] else ""
        click.echo(f"\nSchedule ID: {idx}{active}")

        headers = ["Day", "Active"]
        click.echo(
            tabulate(
                [
                    [key.capitalize(), program[f"programActivation{key.capitalize()}"]]
                    for key in DAYS_OF_WEEK
                ],
                headers=headers,
            )
        )


async def _get_schedule(
    ctx_data: dict[str, Any],
    websession: aiohttp.ClientSession,
    id: int,
) -> tuple[RenaultVehicle, list[ChargeSchedule], ChargeSchedule]:
    """Get the given schedules activated-flag to given state."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response_data = await vehicle._get_vehicle_data("charging-settings")
    response = cast(
        KamereonVehicleChargingSettingsData,
        response_data.get_attributes(KamereonVehicleChargingSettingsDataSchema),
    )

    if not response.schedules:
        raise ValueError("No schedules found.")

    schedule = next(
        (schedule for schedule in response.schedules if id == schedule.id), None
    )
    if schedule:
        return (vehicle, response.schedules, schedule)

    raise IndexError(f"Schedule id {id} not found.")


@schedule.command()
@click.argument("id", type=int)
@helpers.days_of_week_option(
    helptext="{} schedule in format `hh:mm,duration` (for local timezone) "
    "or `Thh:mmZ,duration` (for utc) or `clear` to unset."
)
@click.pass_obj
@helpers.coro_with_websession
async def set(
    ctx_data: dict[str, Any],
    *,
    id: int,
    websession: aiohttp.ClientSession,
    **kwargs: Any,
) -> None:
    """Update charging schedule {ID}."""
    vehicle, schedules, schedule = await _get_schedule(
        websession=websession, ctx_data=ctx_data, id=id
    )

    update_settings(schedule, **kwargs)

    write_response = await vehicle.set_charge_schedules(schedules)
    click.echo(write_response.raw_data)


@schedule.command()
@click.argument("id", type=int)
@click.pass_obj
@helpers.coro_with_websession
async def activate(
    ctx_data: dict[str, Any],
    *,
    id: int,
    websession: aiohttp.ClientSession,
) -> None:
    """Activate charging schedule {ID}."""
    vehicle, schedules, schedule = await _get_schedule(
        websession=websession, ctx_data=ctx_data, id=id
    )

    schedule.activated = True

    write_response = await vehicle.set_charge_schedules(schedules)
    click.echo(write_response.raw_data)


@schedule.command()
@click.argument("id", type=int)
@click.pass_obj
@helpers.coro_with_websession
async def deactivate(
    ctx_data: dict[str, Any],
    *,
    id: int,
    websession: aiohttp.ClientSession,
) -> None:
    """Deactivate charging schedule {ID}."""
    vehicle, schedules, schedule = await _get_schedule(
        websession=websession, ctx_data=ctx_data, id=id
    )

    schedule.activated = False

    write_response = await vehicle.set_charge_schedules(schedules)
    click.echo(write_response.raw_data)


def update_settings(
    schedule: ChargeSchedule,
    **kwargs: Any,
) -> None:
    """Update charging settings."""
    for day in DAYS_OF_WEEK:
        if day in kwargs:
            day_value = kwargs.pop(day)

            if day_value == "clear":
                setattr(schedule, day, None)
            elif day_value:
                start_time, duration = _parse_day_schedule(str(day_value))
                setattr(
                    schedule,
                    day,
                    ChargeDaySchedule(
                        raw_data={}, startTime=start_time, duration=duration
                    ),
                )


def _parse_day_schedule(raw: str) -> tuple[str, int]:
    match = _DAY_SCHEDULE_REGEX.match(raw)
    if not match:
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Should be of the form HH:MM,DURATION or THH:MMZ,DURATION"
        )

    hours = int(match.group("hours"))
    if hours >= _HOURS_PER_DAY:
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Hours should be less than 24."
        )
    minutes = int(match.group("minutes"))
    if (minutes % 15) != 0:
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Minutes should be a multiple of 15."
        )
    duration = int(match.group("duration"))
    if (duration % 15) != 0:
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Duration should be a multiple of 15."
        )
    if match.group("prefix") and match.group("suffix"):
        formatted_start_time = f"T{hours:02g}:{minutes:02g}Z"
    elif not (match.group("prefix") or match.group("suffix")):
        formatted_start_time = helpers.convert_minutes_to_tztime(hours * 60 + minutes)
    else:
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "If provided, both T and Z must be set."
        )
    return (formatted_start_time, duration)
