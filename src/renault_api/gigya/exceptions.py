"""Gigya exceptions."""

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


class PendingTwoFactorAuthenticationException(GigyaResponseException):
    """Account requires two-factor authentication (Gigya errorCode 403101).

    See https://github.com/hacf-fr/renault-api/issues/2132 for background on
    when Gigya started enforcing this. Catch this exception after calling
    `RenaultSession.login`, then drive the challenge with
    `RenaultSession.request_two_factor_auth_code` and
    `RenaultSession.complete_two_factor_auth`.
    """

    def __init__(self, error_code: int, error_details: str | None, reg_token: str):
        """Initialise PendingTwoFactorAuthenticationException."""
        super().__init__(error_code, error_details)
        self.reg_token = reg_token
