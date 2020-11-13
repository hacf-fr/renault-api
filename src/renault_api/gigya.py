"""Gigya client for authentication."""
import logging
from typing import Any
from typing import Dict
from typing import Optional

import jwt
from aiohttp import ClientSession

from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from .dataclass import JWTInfo
from .exceptions import GigyaException
from .exceptions import GigyaResponseException

_LOGGER = logging.getLogger(__name__)


class Gigya(object):
    """Gigya client for authentication."""

    def __init__(
        self, websession: ClientSession, locale_details: Dict[str, str]
    ) -> None:
        """Initialise Gigya."""
        self._websession = websession

        self._api_key = locale_details[CONF_GIGYA_APIKEY]
        self._root_url = locale_details[CONF_GIGYA_URL]
        self._person_id: Optional[str] = None
        self._cookie_value: Optional[str] = None
        self._jwt_token: Optional[JWTInfo] = None

    async def _request(self, method: str, path: str, data: Any) -> Any:
        url = self._root_url + path
        async with self._websession.request(method, url, data=data) as response:
            response_text = await response.text()
            _LOGGER.debug(
                "Received Gigya response %s on %s: %s",
                response.status,
                url,
                response_text,
            )
            response_json = await response.json(content_type="text/javascript")
            _raise_gigya_errors(response_json)
            response.raise_for_status()

            return response_json

    async def login_raw(self, data: Any) -> Any:
        """Send login to Gigya."""
        return await self._request(
            "POST",
            "/accounts.login",
            data=data,
        )

    async def login(self, user: str, password: str) -> Any:
        """Send login to Gigya."""
        data = {
            "ApiKey": self._api_key,
            "loginID": user,
            "password": password,
        }
        response_json = await self.login_raw(data)

        self._cookie_value = response_json.get("sessionInfo", {}).get("cookieValue")

        if not self._cookie_value:
            raise GigyaException(
                "Unable to find Gigya cookieValue from login response! "
                "Response included keys %s",
                ", ".join(response_json.keys()),
            )
        return response_json

    async def get_account_info_raw(self, data: Any) -> Any:
        """Get account info."""
        return await self._request(
            "POST",
            "/accounts.getAccountInfo",
            data=data,
        )

    async def get_person_id(self) -> str:
        """Get person id."""
        current_person_id = self._person_id

        if current_person_id:
            return current_person_id

        data = {
            "ApiKey": self._api_key,
            "login_token": self._cookie_value,
        }
        response_json = await self.get_account_info_raw(data)

        current_person_id = response_json.get("data", {}).get("personId")

        if not current_person_id:
            raise GigyaException(
                "Unable to find Gigya person ID from account info!"
                "Response contained keys %s",
                ", ".join(response_json.keys()),
            )
        self._person_id = current_person_id
        return current_person_id

    async def get_jwt_raw(self, data: Any) -> Any:
        """Get JWT token."""
        return await self._request(
            "POST",
            "/accounts.getJWT",
            data=data,
        )

    async def get_jwt(self) -> str:
        """Get JWT token."""
        current_token = self._jwt_token
        if current_token and not current_token.has_expired():
            return current_token.value

        data = {
            "ApiKey": self._api_key,
            "login_token": self._cookie_value,
            "fields": "data.personId,data.gigyaDataCenter",
            "expiration": 900,
        }
        response_json = await self.get_jwt_raw(data)

        new_token: str = response_json.get("id_token")

        if not new_token:
            raise GigyaException(
                "Unable to find Gigya JWT token in response: %s", response_json
            )

        decoded = jwt.decode(new_token, options={"verify_signature": False})
        self._jwt_token = JWTInfo(new_token, decoded["exp"])
        return new_token


def _raise_gigya_errors(response_json: Any) -> None:
    if response_json.get("errorCode", 0) > 0:
        raise GigyaResponseException(response_json)
