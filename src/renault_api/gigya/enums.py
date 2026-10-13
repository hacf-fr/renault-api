"""Gigya enums."""

from enum import IntEnum


class GigyaErrorCode(IntEnum):
    """Enum for Gigya error codes."""

    INVALID_VERIFICATION_CODE = 400006
    PENDING_TWO_FACTOR_AUTHENTICATION = 403101
