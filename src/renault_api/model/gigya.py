"""Gigya models."""
from dataclasses import dataclass
from dataclasses import field
from typing import Optional

import marshmallow_dataclass

from . import BaseSchema
from renault_api.exceptions import GigyaResponseException


@dataclass
class GigyaResponse:
    """Gigya response."""

    error_code: int = field(metadata=dict(data_key="errorCode"))
    error_details: Optional[str] = field(metadata=dict(data_key="errorDetails"))

    def raise_for_error_code(self) -> None:
        """Checks the response information."""
        if self.error_code > 0:
            raise GigyaResponseException(self.error_code, self.error_details)


@dataclass
class GigyaLoginSessionInfo:
    """Gigya Login sessionInfo data."""

    cookie_value: Optional[str] = field(metadata=dict(data_key="cookieValue"))


@dataclass
class GigyaLoginResponse(GigyaResponse):
    """Gigya response to POST on /accounts.login."""

    session_info: Optional[GigyaLoginSessionInfo] = field(
        metadata=dict(data_key="sessionInfo")
    )


@dataclass
class GigyaGetAccountInfoData:
    """Gigya Login sessionInfo data."""

    person_id: Optional[str] = field(metadata=dict(data_key="personId"))


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
