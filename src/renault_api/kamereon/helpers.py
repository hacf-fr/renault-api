"""Helpers for Kamereon models."""
from __future__ import annotations

from typing import Any
from typing import Dict

from . import models


_DAYS = [
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
    for day in _DAYS:
        if day in settings.keys():
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
