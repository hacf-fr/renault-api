"""Gigya client for authentication."""
import logging
from typing import Any
from typing import cast
from typing import Dict

from aiohttp import ClientSession
from marshmallow.schema import Schema

from renault_api.model import gigya as model

_LOGGER = logging.getLogger(__name__)


class Gigya:
    """Gigya client for authentication."""

    def __init__(self, websession: ClientSession) -> None:
        """Initialise Gigya."""
        self._websession = websession

    async def _post(
        self, url: str, data: Dict[str, Any], schema: Schema
    ) -> model.GigyaResponse:
        async with self._websession.request("POST", url, data=data) as http_response:
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

    async def login(
        self, root_url: str, api_key: str, login_id: str, password: str
    ) -> model.GigyaLoginResponse:
        """POST to /accounts.login."""
        return cast(
            model.GigyaLoginResponse,
            await self._post(
                f"{root_url}/accounts.login",
                data={
                    "ApiKey": api_key,
                    "loginID": login_id,
                    "password": password,
                },
                schema=model.GigyaLoginResponseSchema,
            ),
        )

    async def get_account_info(
        self, root_url: str, api_key: str, login_token: str
    ) -> model.GigyaGetAccountInfoResponse:
        """POST to /accounts.getAccountInfo."""
        return cast(
            model.GigyaGetAccountInfoResponse,
            await self._post(
                f"{root_url}/accounts.getAccountInfo",
                data={"ApiKey": api_key, "login_token": login_token},
                schema=model.GigyaGetAccountInfoResponseSchema,
            ),
        )

    async def get_jwt(
        self, root_url: str, api_key: str, login_token: str
    ) -> model.GigyaGetJWTResponse:
        """POST to /accounts.getAccountInfo."""
        return cast(
            model.GigyaGetJWTResponse,
            await self._post(
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
