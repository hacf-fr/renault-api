"""Exceptions for Renault API."""


from typing import Optional


class RenaultException(Exception):
    """Base class for Renault API errors."""

    pass


# Gigya exceptions
class GigyaException(RenaultException):
    """Base exception for Gigya errors."""

    pass


class GigyaResponseException(GigyaException):
    """Gigya returned a parsable errors."""

    def __init__(self, error_code: int, error_details: Optional[str]):
        """Initialise GigyaResponseException."""
        self.error_code = error_code
        self.error_details = error_details
