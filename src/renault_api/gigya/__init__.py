"""Gigya API."""
import logging
from json import JSONDecodeError
from typing import Any
from typing import cast
from typing import Dict

import aiohttp
from marshmallow.schema import Schema

from . import models
from . import schemas
from .exceptions import GigyaException

GIGYA_JWT = "gigya_jwt"
GIGYA_LOGIN_TOKEN = "gigya_login_token"  # noqa: S105
GIGYA_PERSON_ID = "gigya_person_id"
GIGYA_KEYS = [GIGYA_JWT, GIGYA_LOGIN_TOKEN, GIGYA_PERSON_ID]

_LOGGER = logging.getLogger(__name__)


async def request(
    websession: aiohttp.ClientSession,
    method: str,
    url: str,
    data: Dict[str, Any],
    schema: Schema,
) -> models.GigyaResponse:
    """Send request to Gigya."""
    async with websession.request(method, url, data=data) as http_response:
        response_text = await http_response.text()
        # Disable logging on Gigya, to avoid unnecessary exposure.
        # _LOGGER.debug(
        #    "Received Gigya response %s on %s: %s",
        #    http_response.status,
        #    url,
        #    response_text,
        # )
        try:
            gigya_response: models.GigyaResponse = schema.loads(response_text)
        except JSONDecodeError as err:
            raise GigyaException("Gigya responded with invalid JSON") from err
        # Check for Gigya error
        gigya_response.raise_for_error_code()
        # Check for HTTP error
        http_response.raise_for_status()

        return gigya_response


async def login(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_id: str,
    password: str,
) -> models.GigyaLoginResponse:
    """Send POST to /accounts.login."""
    return cast(
        models.GigyaLoginResponse,
        await request(
            websession,
            "POST",
            f"{root_url}/accounts.login",
            data={
                "ApiKey": api_key,
                "loginID": login_id,
                "password": password,
            },
            schema=schemas.GigyaLoginResponseSchema,
        ),
    )


async def get_account_info(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_token: str,
) -> models.GigyaGetAccountInfoResponse:
    """Send POST to /accounts.getAccountInfo."""
    return cast(
        models.GigyaGetAccountInfoResponse,
        await request(
            websession,
            "POST",
            f"{root_url}/accounts.getAccountInfo",
            data={
                "ApiKey": api_key,
                "login_token": login_token,
            },
            schema=schemas.GigyaGetAccountInfoResponseSchema,
        ),
    )


async def get_jwt(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_token: str,
) -> models.GigyaGetJWTResponse:
    """Send POST to /accounts.getJWT."""
    return cast(
        models.GigyaGetJWTResponse,
        await request(
            websession,
            "POST",
            f"{root_url}/accounts.getJWT",
            data={
                "ApiKey": api_key,
                "login_token": login_token,
                # gigyaDataCenter may be needed for future jwt validation
                "fields": "data.personId,data.gigyaDataCenter",
                "expiration": 900,
            },
            schema=schemas.GigyaGetJWTResponseSchema,
        ),
    )
