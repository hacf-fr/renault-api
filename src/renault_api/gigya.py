"""Gigya client for authentication."""
import logging
from typing import Any
from typing import cast
from typing import Dict

from aiohttp import ClientSession
from marshmallow.schema import Schema

from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from renault_api.model import gigya as model

_LOGGER = logging.getLogger(__name__)


class Gigya:
    """Gigya client for authentication."""

    def __init__(
        self, websession: ClientSession, locale_details: Dict[str, str]
    ) -> None:
        """Initialise Gigya."""
        self._websession = websession

        self._api_key = locale_details[CONF_GIGYA_APIKEY]
        self._root_url = locale_details[CONF_GIGYA_URL]

    async def _post(
        self, path: str, data: Dict[str, Any], schema: Schema
    ) -> model.GigyaResponse:
        url = f"{self._root_url}{path}"
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

    async def login(self, login_id: str, password: str) -> model.GigyaLoginResponse:
        """POST to /accounts.login."""
        return cast(
            model.GigyaLoginResponse,
            await self._post(
                "/accounts.login",
                data={
                    "ApiKey": self._api_key,
                    "loginID": login_id,
                    "password": password,
                },
                schema=model.GigyaLoginResponseSchema,
            ),
        )

    async def get_account_info(
        self, login_token: str
    ) -> model.GigyaGetAccountInfoResponse:
        """POST to /accounts.getAccountInfo."""
        return cast(
            model.GigyaGetAccountInfoResponse,
            await self._post(
                "/accounts.getAccountInfo",
                data={"ApiKey": self._api_key, "login_token": login_token},
                schema=model.GigyaGetAccountInfoResponseSchema,
            ),
        )

    async def get_jwt(self, login_token: str) -> model.GigyaGetJWTResponse:
        """POST to /accounts.getAccountInfo."""
        return cast(
            model.GigyaGetJWTResponse,
            await self._post(
                "/accounts.getJWT",
                data={
                    "ApiKey": self._api_key,
                    "login_token": login_token,
                    # gigyaDataCenter may be needed for future jwt validation
                    "fields": "data.personId,data.gigyaDataCenter",
                    "expiration": 900,
                },
                schema=model.GigyaGetJWTResponseSchema,
            ),
        )
