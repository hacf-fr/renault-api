"""Gigya models."""

from dataclasses import dataclass
from typing import Any

from . import exceptions
from renault_api.models import BaseModel

COMMON_ERRRORS: list[dict[str, Any]] = [
    {
        "errorCode": 403042,
        "error_type": exceptions.InvalidCredentialsException,
    }
]


TFA_PENDING_ERROR_CODE = 403101


@dataclass
class GigyaResponse(BaseModel):
    """Gigya response."""

    errorCode: int
    errorDetails: str | None
    regToken: str | None

    def raise_for_error_code(self) -> None:
        """Checks the response information."""
        if self.errorCode > 0:
            if self.errorCode == TFA_PENDING_ERROR_CODE and self.regToken:
                raise exceptions.PendingTwoFactorAuthenticationException(
                    self.errorCode, self.errorDetails, self.regToken
                )
            for common_error in COMMON_ERRRORS:
                if self.errorCode == common_error["errorCode"]:
                    error_type = common_error["error_type"]
                    raise error_type(self.errorCode, self.errorDetails)
            raise exceptions.GigyaResponseException(self.errorCode, self.errorDetails)


@dataclass
class GigyaLoginSessionInfo(BaseModel):
    """Gigya Login sessionInfo details."""

    cookieValue: str | None


@dataclass
class GigyaLoginResponse(GigyaResponse):
    """Gigya response to POST on /accounts.login."""

    sessionInfo: GigyaLoginSessionInfo | None

    def get_session_cookie(self) -> str:
        """Return cookie value from session information."""
        if not self.sessionInfo:
            raise exceptions.GigyaException("`sessionInfo` is None in Login response.")
        if not self.sessionInfo.cookieValue:
            raise exceptions.GigyaException(
                "`sessionInfo.cookieValue` is None in Login response."
            )
        return self.sessionInfo.cookieValue


@dataclass
class GigyaGetAccountInfoData(BaseModel):
    """Gigya GetAccountInfo data details."""

    personId: str | None


@dataclass
class GigyaGetAccountInfoResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getAccountInfo."""

    data: GigyaGetAccountInfoData | None

    def get_person_id(self) -> str:
        """Return person id."""
        if not self.data:
            raise exceptions.GigyaException(
                "`data` is None in GetAccountInfo response."
            )
        if not self.data.personId:
            raise exceptions.GigyaException(
                "`data.personId` is None in GetAccountInfo response."
            )
        return self.data.personId


@dataclass
class GigyaGetJWTResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getJWT."""

    id_token: str | None

    def get_jwt(self) -> str:
        """Return jwt token."""
        if not self.id_token:
            raise exceptions.GigyaException("`id_token` is None in GetJWT response.")
        return self.id_token


@dataclass
class GigyaTfaInitResponse(GigyaResponse):
    """Gigya response to GET on /accounts.tfa.initTFA."""

    gigyaAssertion: str | None

    def get_gigya_assertion(self) -> str:
        """Return the assertion identifying this TFA challenge."""
        if not self.gigyaAssertion:
            raise exceptions.GigyaException(
                "`gigyaAssertion` is None in initTFA response."
            )
        return self.gigyaAssertion


@dataclass
class GigyaTfaEmail(BaseModel):
    """A single email address registered for TFA verification."""

    id: str | None


@dataclass
class GigyaTfaEmailListResponse(GigyaResponse):
    """Gigya response to GET on /accounts.tfa.email.getEmails."""

    emails: list[GigyaTfaEmail] | None

    def get_email_id(self) -> str:
        """Return the id of the (first) registered email address."""
        if not self.emails or not self.emails[0].id:
            raise exceptions.GigyaException(
                "`emails` is empty in TFA email list response."
            )
        return self.emails[0].id


@dataclass
class GigyaTfaSendEmailCodeResponse(GigyaResponse):
    """Gigya response to GET on /accounts.tfa.email.sendVerificationCode."""

    phvToken: str | None

    def get_phv_token(self) -> str:
        """Return the token identifying the sent verification email."""
        if not self.phvToken:
            raise exceptions.GigyaException(
                "`phvToken` is None in sendVerificationCode response."
            )
        return self.phvToken


@dataclass
class GigyaTfaEmailCompleteVerificationResponse(GigyaResponse):
    """Gigya response to GET on /accounts.tfa.email.completeVerification."""

    providerAssertion: str | None

    def get_provider_assertion(self) -> str:
        """Return the assertion proving the emailed code was verified."""
        if not self.providerAssertion:
            raise exceptions.GigyaException(
                "`providerAssertion` is None in completeVerification response."
            )
        return self.providerAssertion
