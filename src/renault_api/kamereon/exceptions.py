"""Exceptions for Renault API."""
from typing import Optional

from renault_api.exceptions import RenaultException


class KamereonException(RenaultException):
    """Base exception for Kamereon errors."""

    pass


class KamereonResponseException(KamereonException):
    """Kamereon returned a parsable errors."""

    def __init__(self, error_code: Optional[str], error_details: Optional[str]):
        """Initialise KamereonResponseException."""
        self.error_code = error_code
        self.error_details = error_details
