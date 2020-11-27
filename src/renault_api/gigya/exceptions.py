"""Exceptions for Gigya API."""
from typing import Optional


class GigyaException(Exception):
    """Base exception for Gigya errors."""

    pass


class GigyaResponseException(GigyaException):
    """Gigya returned a parsable errors."""

    def __init__(self, error_code: int, error_details: Optional[str]):
        """Initialise GigyaResponseException."""
        self.error_code = error_code
        self.error_details = error_details
