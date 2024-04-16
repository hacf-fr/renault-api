"""Gigya exceptions."""

from __future__ import annotations

from renault_api.exceptions import RenaultException


class GigyaException(RenaultException):
    """Base exception for Gigya errors."""

    pass


class GigyaResponseException(GigyaException):
    """Gigya returned a parsable errors."""

    def __init__(self, error_code: int, error_details: str | None):
        """Initialise GigyaResponseException."""
        self.error_code = error_code
        self.error_details = error_details


class InvalidCredentialsException(GigyaResponseException):
    """Invalid loginID or password."""

    pass
