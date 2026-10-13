"""Gigya exceptions."""

from renault_api.exceptions import RenaultException


class GigyaException(RenaultException):
    """Base exception for Gigya errors."""

    pass


class GigyaResponseException(GigyaException):
    """Gigya returned a parsable errors."""

    def __init__(self, error_code: int, error_details: str | None):
        """Initialise GigyaResponseException."""
        super().__init__(error_code, error_details)
        self.error_code = error_code
        self.error_details = error_details


class InvalidCredentialsException(GigyaResponseException):
    """Invalid loginID or password."""

    pass


class InvalidVerificationCodeException(GigyaResponseException):
    """Wrong two-factor authentication code (Gigya errorCode 400006).

    Only raised when completing the email verification: the same challenge
    can be retried with the right code.
    """

    pass


class PendingTwoFactorAuthenticationException(GigyaResponseException):
    """Account requires two-factor authentication (Gigya errorCode 403101).

    See https://github.com/hacf-fr/renault-api/issues/2132 for background on
    when Gigya started enforcing this. `reg_token` is needed to start the
    two-factor authentication challenge.
    """

    def __init__(self, error_code: int, error_details: str | None, reg_token: str):
        """Initialise PendingTwoFactorAuthenticationException.

        `reg_token` is kept out of `args`, so that it doesn't appear in
        `str()`/`repr()` of the exception, or in logged tracebacks.
        """
        super().__init__(error_code, error_details)
        self.reg_token = reg_token
