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

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle
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


@click.group()
def schedule() -> None:
    """Display or update charging schedules."""
    pass


@schedule.command()
@click.option("--id", type=int, help="Schedule ID")
@click.pass_obj
@helpers.coro_with_websession
async def show(
    ctx_data: Dict[str, Any],
    *,
    id: Optional[int] = None,
    websession: aiohttp.ClientSession,
    **kwargs: Any,
) -> None:
    """Display charging settings."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charging_settings()

    # Display mode
    click.echo(f"Mode: {response.mode}")
    if not response.schedules:  # pragma: no cover
        click.echo("No schedules found.")
        return

    for schedule in response.schedules:
        if id and id != schedule.id:
            continue
        click.echo(
            f"\nSchedule ID: {schedule.id}{' [Active]' if schedule.activated else ''}"
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


@schedule.command()
@click.option("--id", type=int, help="Schedule ID")
@helpers.days_of_week_option(
    helptext="{} schedule in format `hh:mm,duration` (for local timezone) "
    "or `Thh:mmZ,duration` (for utc) or `clear` to unset."
)
@click.pass_obj
@helpers.coro_with_websession
async def set(
    ctx_data: Dict[str, Any],
    *,
    id: Optional[int] = None,
    websession: aiohttp.ClientSession,
    **kwargs: Any,
) -> None:
    """Display charging settings."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charging_settings()

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
