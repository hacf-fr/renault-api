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


# Kamereon exceptions
class KamereonException(RenaultException):
    """Base exception for Kamereon errors."""

    pass


class KamereonResponseException(KamereonException):
    """Kamereon returned a parsable errors."""

    def __init__(self, error_code: Optional[str], error_details: Optional[str]):
        """Initialise KamereonResponseException."""
        self.error_code = error_code
        self.error_details = error_details
