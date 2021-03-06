"""Helpers for Kamereon models."""
from __future__ import annotations

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from . import models
from renault_api.kamereon.exceptions import ModelValidationException

DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

MINUTES_PER_DAY = 60 * 24


def update_schedule(schedule: models.ChargeSchedule, settings: Dict[str, Any]) -> None:
    """Update schedule."""
    if "activated" in settings:
        schedule.activated = settings["activated"]
    for day in DAYS_OF_WEEK:
        if day in settings:
            day_settings = settings[day]

            if day_settings:  # pragma: no branch
                start_time = day_settings["startTime"]
                duration = day_settings["duration"]

                setattr(
                    schedule,
                    day,
                    models.ChargeDaySchedule(day_settings, start_time, duration),
                )


def create_schedule(
    settings: Dict[str, Any]
) -> models.ChargeSchedule:  # pragma: no cover
    """Update schedule."""
    raise NotImplementedError


def get_end_time(start_time: str, duration: Optional[int] = None) -> str:
    """Compute end time."""
    total_minutes = get_total_minutes(start_time, duration)
    return format_time(total_minutes)


def format_time(total_minutes: int) -> str:
    """Format time."""
    end_hours, end_minutes = divmod(total_minutes, 60)
    end_hours = end_hours % 24
    return f"T{end_hours:02g}:{end_minutes:02g}Z"


def get_total_minutes(start_time: Optional[str], duration: Optional[int] = None) -> int:
    """Get total minutes from a `Thh:mmZ` formatted time."""
    if not start_time:  # pragma: no cover
        return 0
    return int(start_time[1:3]) * 60 + int(start_time[4:6]) + (duration or 0)


def validate_charge_schedules(schedules: List[models.ChargeSchedule]) -> None:
    """Validate a list of ChargeSchedule."""
    for schedule in schedules:  # pragma: no branch
        validate_charge_schedule(schedule)


def validate_charge_schedule(schedule: models.ChargeSchedule) -> None:
    """Validate a ChargeSchedule."""
    for day in DAYS_OF_WEEK:  # pragma: no branch
        day_schedule: models.ChargeDaySchedule = getattr(schedule, day)
        if day_schedule:  # pragma: no branch
            try:
                validate_charge_day_schedule(day_schedule)
                end_time = get_total_minutes(
                    day_schedule.startTime, day_schedule.duration
                )
                if end_time > MINUTES_PER_DAY:
                    # Spans midnight, so we need to compare to next day schedule
                    next_day_schedule: models.ChargeDaySchedule = getattr(
                        schedule, get_next_day(day)
                    )
                    if next_day_schedule:  # pragma: no branch
                        prevent_overlap(end_time, next_day_schedule)
            except ModelValidationException as ex:
                raise ModelValidationException(
                    f"Invalid charge settings for {day}: {ex}"
                ) from ex


def validate_charge_day_schedule(schedule: models.ChargeDaySchedule) -> None:
    """Validate a ChargeDaySchedule."""
    validate_start_time(schedule.startTime)
    validate_duration(schedule.duration)


def validate_start_time(start_time: Any) -> None:
    """Validate a charge start time."""
    if (
        isinstance(start_time, str)
        and len(start_time) == 7
        and start_time[0] == "T"
        and start_time[3] == ":"
        and start_time[6] == "Z"
        and 0 <= int(start_time[1:3]) < 24
        and start_time[4:6] in ["00", "15", "30", "45"]
    ):
        return
    raise ModelValidationException(f"`{start_time}` is not a valid start time.")


def validate_duration(duration: Any) -> None:
    """Validate a charge duration."""
    if isinstance(duration, int) and duration > 0 and duration % 15 == 0:
        return
    raise ModelValidationException(f"`{duration}` is not a valid duration.")


def prevent_overlap(
    end_time: int, next_start_time: Union[int, models.ChargeDaySchedule]
) -> None:
    """Prevent overlap."""
    end_time = end_time % MINUTES_PER_DAY
    if isinstance(next_start_time, models.ChargeDaySchedule):  # pragma: no branch
        next_start_time = get_total_minutes(next_start_time.startTime)
    if end_time >= next_start_time:  # pragma: no branch
        raise ModelValidationException(
            f"`{format_time(end_time)}` end time overlaps with next day schedule."
        )


def get_next_day(day: str) -> str:
    """Get the next day end time."""
    return DAYS_OF_WEEK[(DAYS_OF_WEEK.index(day) + 1) % len(DAYS_OF_WEEK)]
