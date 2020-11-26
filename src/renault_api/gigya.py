"""Gigya client for authentication."""
import logging
from typing import Any
from typing import cast
from typing import Dict

import aiohttp
from aiohttp import ClientSession
from marshmallow.schema import Schema

from renault_api.model import gigya as model

_LOGGER = logging.getLogger(__name__)


async def gigya_request(
    websession: aiohttp.ClientSession,
    method: str,
    url: str,
    data: Dict[str, Any],
    schema: Schema,
) -> model.GigyaResponse:
    """Send request to Gigya."""
    async with websession.request(method, url, data=data) as http_response:
        response_text = await http_response.text()
        _LOGGER.debug(
            "Received Gigya response %s on %s: %s",
            http_response.status,
            url,
            response_text,
        )
        gigya_response: model.GigyaResponse = schema.loads(response_text)
        # Check for Gigya error
        gigya_response.raise_for_error_code()
        # Check for HTTP error
        http_response.raise_for_status()

        return gigya_response


async def gigya_login(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_id: str,
    password: str,
) -> model.GigyaLoginResponse:
    """Send POST to /accounts.login."""
    return cast(
        model.GigyaLoginResponse,
        await gigya_request(
            websession,
            "POST",
            f"{root_url}/accounts.login",
            data={
                "ApiKey": api_key,
                "loginID": login_id,
                "password": password,
            },
            schema=model.GigyaLoginResponseSchema,
        ),
    )


async def gigya_get_account_info(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_token: str,
) -> model.GigyaGetAccountInfoResponse:
    """Send POST to /accounts.getAccountInfo."""
    return cast(
        model.GigyaGetAccountInfoResponse,
        await gigya_request(
            websession,
            "POST",
            f"{root_url}/accounts.getAccountInfo",
            data={
                "ApiKey": api_key,
                "login_token": login_token,
            },
            schema=model.GigyaGetAccountInfoResponseSchema,
        ),
    )


async def gigya_get_jwt(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_token: str,
) -> model.GigyaGetJWTResponse:
    """Send POST to /accounts.getAccountInfo."""
    return cast(
        model.GigyaGetJWTResponse,
        await gigya_request(
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
            schema=model.GigyaGetJWTResponseSchema,
        ),
    )


class Gigya:
    """Gigya client for authentication."""

    def __init__(self, websession: ClientSession, root_url: str, api_key: str) -> None:
        """Initialise Gigya."""
        self._websession = websession
        self._root_url = root_url
        self._api_key = api_key

    async def login(self, login_id: str, password: str) -> model.GigyaLoginResponse:
        """POST to /accounts.login."""
        return await gigya_login(
            self._websession,
            self._root_url,
            self._api_key,
            login_id,
            password,
        )

    async def get_account_info(
        self, login_token: str
    ) -> model.GigyaGetAccountInfoResponse:
        """POST to /accounts.getAccountInfo."""
        return await gigya_get_account_info(
            self._websession,
            self._root_url,
            self._api_key,
            login_token,
        )

    async def get_jwt(self, login_token: str) -> model.GigyaGetJWTResponse:
        """POST to /accounts.getAccountInfo."""
        return await gigya_get_jwt(
            self._websession,
            self._root_url,
            self._api_key,
            login_token,
        )
