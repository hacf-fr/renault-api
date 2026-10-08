"""Gigya enums."""

from enum import IntEnum


class GigyaErrorCode(IntEnum):
    """Enum for Gigya error codes."""

    PENDING_TWO_FACTOR_AUTHENTICATION = 403101
