"""Kamereon exceptions."""
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


class AccessDeniedException(KamereonResponseException):
    """Access is denied for this resource."""

    pass


class NotSupportedException(KamereonResponseException):
    """This feature is not technically supported by this gateway."""

    pass


class InvalidUpstreamException(KamereonResponseException):
    """Invalid response from the upstream server."""

    pass


class QuotaLimitException(KamereonResponseException):
    """You have reached your quota limit."""

    pass


class InvalidInputException(KamereonResponseException):
    """The input is invalid."""

    pass


class ResourceNotFoundException(KamereonResponseException):
    """Resource not found."""

    pass


class FailedForwardException(KamereonResponseException):
    """Failed to forward request to remote service."""

    pass
