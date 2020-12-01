"""Kamereon enums."""
from enum import Enum


class ChargeState(Enum):
    """Enum for battery-status charge state."""

    NOT_IN_CHARGE = 0.0
    WAITING_FOR_PLANNED_CHARGE = 0.1
    CHARGE_ENDED = 0.2
    WAITING_FOR_CURRENT_CHARGE = 0.3
    ENERGY_FLAP_OPENED = 0.4
    CHARGE_IN_PROGRESS = 1.0
    # This next is more accurately "not charging" (<= ZE40) or "error" (ZE50).
    CHARGE_ERROR = -1.0
    NOT_AVAILABLE = -1.1


class PlugState(Enum):
    """Enum for battery-status plug state."""

    UNPLUGGED = 0
    PLUGGED = 1
    PLUG_ERROR = -1
    NOT_AVAILABLE = -2147483648


class ChargeMode(Enum):
    """Enum for charge-mode."""

    ALWAYS = "always"
    ALWAYS_CHARGING = "always_charging"
    SCHEDULE_MODE = "schedule_mode"
