"""Helpers for Kamereon models."""

from __future__ import annotations

from typing import Any
from warnings import warn

from . import models

DAYS_OF_WEEK = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


def update_schedule(
    schedule: models.ChargeSchedule, settings: dict[str, Any]
) -> None:  # pragma: no cover
    """Update charge schedule."""
    warn(
        "This method is deprecated, please use update_charge_schedule.",
        DeprecationWarning,
        stacklevel=2,
    )
    update_charge_schedule(schedule, settings)


def update_charge_schedule(
    schedule: models.ChargeSchedule, settings: dict[str, Any]
) -> None:
    """Update charge schedule."""
    if "activated" in settings:
        schedule.activated = settings["activated"]
    for day in DAYS_OF_WEEK:
        if day in settings:
            day_settings = settings[day]

            if day_settings is None:
                setattr(schedule, day, None)
            elif day_settings:  # pragma: no branch
                start_time = day_settings["startTime"]
                duration = day_settings["duration"]

                setattr(
                    schedule,
                    day,
                    models.ChargeDaySchedule(day_settings, start_time, duration),
                )


def update_hvac_schedule(
    schedule: models.HvacSchedule, settings: dict[str, Any]
) -> None:
    """Update HVAC schedule."""
    if "activated" in settings:
        schedule.activated = settings["activated"]
    for day in DAYS_OF_WEEK:
        if day in settings:
            day_settings = settings[day]

            if day_settings is None:
                setattr(schedule, day, None)
            elif day_settings:  # pragma: no branch
                ready_at_time = day_settings["readyAtTime"]

                setattr(
                    schedule,
                    day,
                    models.HvacDaySchedule(day_settings, ready_at_time),
                )


def create_schedule(
    settings: dict[str, Any],
) -> models.ChargeSchedule:  # pragma: no cover
    warn(
        "This method is deprecated, please use create_charge_schedule.",
        DeprecationWarning,
        stacklevel=2,
    )
    return create_charge_schedule(settings)


def create_charge_schedule(
    settings: dict[str, Any],
) -> models.ChargeSchedule:  # pragma: no cover
    """Update schedule."""
    raise NotImplementedError


def create_hvac_schedule(
    settings: dict[str, Any],
) -> models.HvacSchedule:  # pragma: no cover
    """Update schedule."""
    raise NotImplementedError


def get_end_time(start_time: str, duration: int | None = None) -> str:
    """Compute end time."""
    total_minutes = get_total_minutes(start_time, duration)
    return format_time(total_minutes)


def format_time(total_minutes: int) -> str:
    """Format time."""
    end_hours, end_minutes = divmod(total_minutes, 60)
    end_hours = end_hours % 24
    return f"T{end_hours:02g}:{end_minutes:02g}Z"


def get_total_minutes(start_time: str | None, duration: int | None = None) -> int:
    """Get total minutes from a `Thh:mmZ` formatted time."""
    if not start_time:  # pragma: no cover
        return 0
    return int(start_time[1:3]) * 60 + int(start_time[4:6]) + (duration or 0)
