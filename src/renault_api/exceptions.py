"""Exceptions for Renault API."""


class RenaultException(Exception):  # noqa: N818
    """Base exception for Renault API errors."""

    pass


class NotAuthenticatedException(RenaultException):  # noqa: N818
    """You are not authenticated, or authentication has expired."""

    pass


class EndpointNotAvailableError(RenaultException):
    """The endpoint is not available for this model."""

    def __init__(self, endpoint: str, model_code: str):
        super().__init__("Endpoint not available")
        self.endpoint = endpoint
        self.model_code = model_code

    def __str__(self):
        return f"Endpoint '{self.endpoint}' not available for model '{self.model_code}'"
