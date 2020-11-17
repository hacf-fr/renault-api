"""Gigya models."""
from dataclasses import dataclass
from typing import Optional

import marshmallow_dataclass

from . import BaseSchema
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


@dataclass
class GigyaGetAccountInfoData:
    """Gigya Login sessionInfo data."""

    personId: Optional[str]  # noqa: N815


@dataclass
class GigyaGetAccountInfoResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getAccountInfo."""

    data: Optional[GigyaGetAccountInfoData]


@dataclass
class GigyaGetJWTResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getJWT."""

    id_token: Optional[str]


GigyaLoginResponseSchema = marshmallow_dataclass.class_schema(
    GigyaLoginResponse, base_schema=BaseSchema
)()
GigyaGetAccountInfoResponseSchema = marshmallow_dataclass.class_schema(
    GigyaGetAccountInfoResponse, base_schema=BaseSchema
)()
GigyaGetJWTResponseSchema = marshmallow_dataclass.class_schema(
    GigyaGetJWTResponse, base_schema=BaseSchema
)()
