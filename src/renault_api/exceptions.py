"""Exceptions for Renault API."""


class RenaultException(Exception):
    """Base exception for Renault API errors."""

    pass


class NotAuthenticatedException(RenaultException):
    """You are not authenticated, or authentication has expired."""

    pass
