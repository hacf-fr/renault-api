"""Gigya models."""

from __future__ import annotations

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


@dataclass
class GigyaResponse(BaseModel):
    """Gigya response."""

    errorCode: int
    errorDetails: str | None

    def raise_for_error_code(self) -> None:
        """Checks the response information."""
        if self.errorCode > 0:
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
        if not self.sessionInfo:  # pragma: no cover
            raise exceptions.GigyaException("`sessionInfo` is None in Login response.")
        if not self.sessionInfo.cookieValue:  # pragma: no cover
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
        if not self.data:  # pragma: no cover
            raise exceptions.GigyaException(
                "`data` is None in GetAccountInfo response."
            )
        if not self.data.personId:  # pragma: no cover
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
        if not self.id_token:  # pragma: no cover
            raise exceptions.GigyaException("`id_token` is None in GetJWT response.")
        return self.id_token
