"""CLI function for a vehicle."""
import re
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import aiohttp
import click
from tabulate import tabulate

from . import helpers
from . import renault_vehicle
from renault_api.kamereon.helpers import DAYS_OF_WEEK
from renault_api.kamereon.models import ChargeDaySchedule
from renault_api.kamereon.models import ChargeSchedule


_DAY_SCHEDULE_REGEX = re.compile(
    "(?P<prefix>T?)"
    "(?P<hours>[0-2][0-9])"
    ":"
    "(?P<minutes>[0-5][0-9])"
    "(?P<suffix>Z?)"
    ","
    "(?P<duration>[0-9]+)"
)


async def charges(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
) -> None:
    """Display charges."""
    parsed_start, parsed_end = helpers.parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charges(start=parsed_start, end=parsed_end)
    charges: List[Dict[str, Any]] = response.raw_data["charges"]
    if not charges:  # pragma: no cover
        click.echo("No data available.")
        return

    headers = [
        "Charge start",
        "Charge end",
        "Duration",
        "Power (kW)",
        "Started at",
        "Finished at",
        "Charge gained",
        "Power level",
        "Status",
    ]
    click.echo(
        tabulate([_format_charges_item(item) for item in charges], headers=headers)
    )


def _format_charges_item(item: Dict[str, Any]) -> List[str]:
    return [
        helpers.get_display_value(item.get("chargeStartDate"), "tzdatetime"),
        helpers.get_display_value(item.get("chargeEndDate"), "tzdatetime"),
        helpers.get_display_value(item.get("chargeDuration"), "minutes"),
        helpers.get_display_value(item.get("chargeStartInstantaneousPower"), "kW"),
        helpers.get_display_value(item.get("chargeStartBatteryLevel"), "%"),
        helpers.get_display_value(item.get("chargeEndBatteryLevel"), "%"),
        helpers.get_display_value(item.get("chargeBatteryLevelRecovered"), "%"),
        helpers.get_display_value(item.get("chargePower")),
        helpers.get_display_value(item.get("chargeEndStatus")),
    ]


async def history(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
    period: Optional[str] = None,
) -> None:
    """Display charge history."""
    parsed_start, parsed_end = helpers.parse_dates(start, end)
    period = period or "month"

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charge_history(
        start=parsed_start, end=parsed_end, period=period
    )
    charge_summaries: List[Dict[str, Any]] = response.raw_data["chargeSummaries"]
    if not charge_summaries:  # pragma: no cover
        click.echo("No data available.")
        return

    headers = [
        period.capitalize(),
        "Number of charges",
        "Total time charging",
        "Errors",
    ]
    click.echo(
        tabulate(
            [_format_charge_history_item(item, period) for item in charge_summaries],
            headers=headers,
        )
    )


def _format_charge_history_item(item: Dict[str, Any], period: str) -> List[str]:
    return [
        helpers.get_display_value(item.get(period)),
        helpers.get_display_value(item.get("totalChargesNumber")),
        helpers.get_display_value(item.get("totalChargesDuration"), "minutes"),
        helpers.get_display_value(item.get("totalChargesErrors")),
    ]


async def mode(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    mode: Optional[str] = None,
) -> None:
    """Display or set charge mode."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    if mode:
        write_response = await vehicle.set_charge_mode(mode)
        click.echo(write_response.raw_data)
    else:
        read_response = await vehicle.get_charge_mode()
        click.echo(f"Charge mode: {read_response.chargeMode}")


async def settings(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    set: bool,
    id: Optional[int] = None,
    **kwargs: Any,
) -> None:
    """Display charging settings."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charging_settings()

    if set:
        id = id or 1
        if not response.schedules:  # pragma: no cover
            click.echo("No schedules found.")
            return

        id_found = False
        for schedule in response.schedules:
            if id == schedule.id:  # pragma: no cover
                update_settings(schedule, **kwargs)
                id_found = True
                break
        if not id_found:
            raise IndexError(f"Schedule id {id} not found.")  # pragma: no cover

        write_response = await vehicle.set_charge_schedules(response.schedules)
        click.echo(write_response.raw_data)
    else:
        # Display mode
        click.echo(f"Mode: {response.mode}")
        if not response.schedules:  # pragma: no cover
            click.echo("No schedules found.")
            return
        for schedule in response.schedules:
            if id and id != schedule.id:  # pragma: no cover
                continue
            click.echo(
                f"Schedule ID: {schedule.id}{' [Active]' if schedule.activated else ''}"
            )

            headers = [
                "Day",
                "Start time",
                "End time",
                "Duration",
            ]
            click.echo(
                tabulate(
                    [_format_charge_schedule(schedule, key) for key in DAYS_OF_WEEK],
                    headers=headers,
                )
            )

            # separate items by additional newline if not last item in list
            if schedule != response.schedules[-1]:
                click.echo("\n")


def _format_charge_schedule(schedule: ChargeSchedule, key: str) -> List[str]:
    details: Optional[ChargeDaySchedule] = getattr(schedule, key)
    if not details:  # pragma: no cover
        return [key, "-", "-", "-"]
    return [
        key.capitalize(),
        helpers.get_display_value(details.startTime, "tztime"),
        helpers.get_display_value(details.get_end_time(), "tztime"),
        helpers.get_display_value(details.duration, "minutes"),
    ]


def update_settings(
    schedule: ChargeSchedule,
    **kwargs: Any,
) -> None:
    """Update charging settings."""
    for day in DAYS_OF_WEEK:
        if day in kwargs:  # pragma: no branch
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


def _parse_day_schedule(raw: str) -> Tuple[str, int]:
    match = _DAY_SCHEDULE_REGEX.match(raw)
    if not match:  # pragma: no cover
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Should be of the form HH:MM,DURATION or THH:MMZ,DURATION"
        )

    hours = int(match.group("hours"))
    if hours > 23:  # pragma: no cover
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Hours should be less than 24."
        )
    minutes = int(match.group("minutes"))
    if (minutes % 15) != 0:  # pragma: no cover
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Minutes should be a multiple of 15."
        )
    duration = int(match.group("duration"))
    if (duration % 15) != 0:  # pragma: no cover
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "Duration should be a multiple of 15."
        )
    if match.group("prefix") and match.group("suffix"):
        formatted_start_time = f"T{hours:02g}:{minutes:02g}Z"
    elif not (match.group("prefix") or match.group("suffix")):
        formatted_start_time = helpers.convert_minutes_to_tztime(hours * 60 + minutes)
    else:  # pragma: no cover
        raise ValueError(
            f"Invalid specification for charge schedule: `{raw}`. "
            "If provided, both T and Z must be set."
        )
    return (formatted_start_time, duration)


async def start(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
) -> None:
    """Start charge."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.set_charge_start()
    click.echo(response.raw_data)
