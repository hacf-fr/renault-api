"""Gigya client for authentication."""
import logging
from typing import Any
from typing import cast
from typing import Dict
from typing import Optional

import aiohttp
from marshmallow.schema import Schema

from .credential_store import CredentialStore
from .exceptions import GigyaException
from .model import gigya as model
from .model.credential import Credential
from .model.credential import JWTCredential

GIGYA_JWT = "gigya_jwt"
GIGYA_LOGIN_TOKEN = "gigya_login_token"
GIGYA_PERSON_ID = "gigya_person_id"
GIGYA_KEYS = [GIGYA_JWT, GIGYA_LOGIN_TOKEN, GIGYA_PERSON_ID]

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

    def __init__(
        self,
        websession: aiohttp.ClientSession,
        root_url: str,
        api_key: str,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise Gigya."""
        self._websession = websession
        self._root_url = root_url
        self._api_key = api_key
        self._credentials: CredentialStore = credential_store or CredentialStore()

    async def login(self, login_id: str, password: str) -> None:
        """Login and cache the login token."""
        self._credentials.clear_keys(GIGYA_KEYS)

        response = await gigya_login(
            self._websession,
            self._root_url,
            self._api_key,
            login_id,
            password,
        )
        self._credentials[GIGYA_LOGIN_TOKEN] = Credential(response.get_session_cookie())

    def _get_login_token(self) -> str:
        login_token = self._credentials.get_value(GIGYA_LOGIN_TOKEN)
        if login_token:
            return login_token
        raise GigyaException(
            f"Credential `{GIGYA_LOGIN_TOKEN}` not found in credential cache."
        )

    async def get_person_id(self) -> str:
        """Get person id."""
        person_id = self._credentials.get_value(GIGYA_PERSON_ID)
        if person_id:
            return person_id
        login_token = self._get_login_token()
        response = await gigya_get_account_info(
            self._websession,
            self._root_url,
            self._api_key,
            login_token,
        )
        person_id = response.get_person_id()
        self._credentials[GIGYA_PERSON_ID] = Credential(person_id)
        return person_id

    async def get_jwt(self) -> str:
        """Get json web token."""
        jwt = self._credentials.get_value(GIGYA_JWT)
        if jwt:
            return jwt
        login_token = self._get_login_token()
        response = await gigya_get_jwt(
            self._websession,
            self._root_url,
            self._api_key,
            login_token,
        )
        jwt = response.get_jwt()
        self._credentials[GIGYA_JWT] = JWTCredential(jwt)
        return jwt
