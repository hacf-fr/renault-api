"""Gigya client for authentication."""
import logging
from typing import Dict

from aiohttp import ClientSession

from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from renault_api.model import gigya as model
from renault_api.model.gigya import GigyaGetAccountInfoData
from renault_api.model.gigya import GigyaLoginSessionInfo

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

    async def login(self, login_id: str, password: str) -> model.GigyaLoginResponse:
        """POST to /accounts.login."""
        return model.GigyaLoginResponse(
            0,
            None,
            GigyaLoginSessionInfo("cookieValue"),
        )

    async def get_account_info(
        self, login_token: str
    ) -> model.GigyaGetAccountInfoResponse:
        """POST to /accounts.getAccountInfo."""
        return model.GigyaGetAccountInfoResponse(
            0,
            None,
            GigyaGetAccountInfoData("person-id"),
        )

    async def get_jwt(self, login_token: str) -> model.GigyaGetJWTResponse:
        """POST to /accounts.getAccountInfo."""
        return model.GigyaGetJWTResponse(
            0,
            None,
            "id_token",
        )
