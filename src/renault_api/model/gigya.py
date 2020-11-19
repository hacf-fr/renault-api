"""Gigya models."""
from dataclasses import dataclass
from typing import Optional

import marshmallow_dataclass

from . import BaseSchema
from renault_api.exceptions import GigyaException
from renault_api.exceptions import GigyaResponseException


@dataclass
class GigyaResponse:
    """Gigya response."""

    errorCode: int  # noqa: N815
    errorDetails: Optional[str]  # noqa: N815

    def raise_for_error_code(self) -> None:
        """Checks the response information."""
        if self.errorCode > 0:
            raise GigyaResponseException(self.errorCode, self.errorDetails)


@dataclass
class GigyaLoginSessionInfo:
    """Gigya Login sessionInfo data."""

    cookieValue: Optional[str]  # noqa: N815


@dataclass
class GigyaLoginResponse(GigyaResponse):
    """Gigya response to POST on /accounts.login."""

    sessionInfo: Optional[GigyaLoginSessionInfo]  # noqa: N815

    def get_session_cookie(self) -> str:
        """Return cookie value from session information."""
        if not self.sessionInfo:  # pragma: no cover
            raise GigyaException("`sessionInfo` is None in Login response.")
        if not self.sessionInfo.cookieValue:  # pragma: no cover
            raise GigyaException("`sessionInfo.cookieValue` is None in Login response.")
        return self.sessionInfo.cookieValue


@dataclass
class GigyaGetAccountInfoData:
    """Gigya Login sessionInfo data."""

    personId: Optional[str]  # noqa: N815


@dataclass
class GigyaGetAccountInfoResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getAccountInfo."""

    data: Optional[GigyaGetAccountInfoData]

    def get_person_id(self) -> str:
        """Return person id."""
        if not self.data:  # pragma: no cover
            raise GigyaException("`data` is None in GetAccountInfo response.")
        if not self.data.personId:  # pragma: no cover
            raise GigyaException("`data.personId` is None in GetAccountInfo response.")
        return self.data.personId


@dataclass
class GigyaGetJWTResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getJWT."""

    id_token: Optional[str]

    def get_jwt_token(self) -> str:
        """Return jwt token."""
        if not self.id_token:  # pragma: no cover
            raise GigyaException("`id_token` is None in GetJWT response.")
        return self.id_token


GigyaLoginResponseSchema = marshmallow_dataclass.class_schema(
    GigyaLoginResponse, base_schema=BaseSchema
)()
GigyaGetAccountInfoResponseSchema = marshmallow_dataclass.class_schema(
    GigyaGetAccountInfoResponse, base_schema=BaseSchema
)()
GigyaGetJWTResponseSchema = marshmallow_dataclass.class_schema(
    GigyaGetJWTResponse, base_schema=BaseSchema
)()
