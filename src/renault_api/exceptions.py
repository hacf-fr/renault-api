"""Exceptions for Renault API."""


class RenaultException(Exception):  # noqa: N818
    """Base exception for Renault API errors."""

    pass


class NotAuthenticatedException(RenaultException):  # noqa: N818
    """You are not authenticated, or authentication has expired."""

    pass
