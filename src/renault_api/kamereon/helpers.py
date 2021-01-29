"""Helpers for Kamereon models."""
from __future__ import annotations

from typing import Any
from typing import Dict
from typing import Optional

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
