"""Client for Renault API."""
from __future__ import annotations

import logging
from typing import Any
from typing import List

from aiohttp import ClientSession

from . import gigya
from . import renault_account
from .const import AVAILABLE_LOCALES
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from renault_api.exceptions import RenaultException


_LOGGER = logging.getLogger(__name__)


class RenaultClient:
    """Proxy to the Renault API."""

    def __init__(self, websession: ClientSession, locale: str) -> None:
        """Initialise Renault Client."""
        self._websession = websession

        locale_details = AVAILABLE_LOCALES.get(locale)
        if not locale_details:
            raise RenaultException(f"Locale {locale} not found in AVAILABLE_LOCALES")

        self._gigya: gigya.Gigya = gigya.Gigya(websession, locale_details)

        self._country = locale[-2:]
        self._kamereon_api_key = locale_details[CONF_KAMEREON_APIKEY]
        self._kamereon_url = locale_details[CONF_KAMEREON_URL]

    async def _request(
        self,
        method: str,
        path: str,
    ) -> Any:
        url = f"{self._kamereon_url}/commerce/v1{path}"
        headers = {
            "apikey": self._kamereon_api_key,
            "x-gigya-id_token": await self._gigya.get_jwt(),
        }
        params = {"country": self._country}

        async with self._websession.request(
            method,
            url,
            headers=headers,
            params=params,
        ) as response:
            response_text = await response.text()
            _LOGGER.debug(
                "Received Kamereon response %s on %s: %s",
                response.status,
                url,
                response_text,
            )
            response_json = await response.json()
            _raise_kamereon_errors(response_json)
            response.raise_for_status()

            return response_json

    async def login(self, user: str, password: str) -> Any:
        """Get API keys for specified locale and load into credential store."""
        return await self._gigya.login(user, password)

    async def get_accounts_raw(self) -> Any:
        """Get list of accounts linked to credentials."""
        gigya_person_id = await self._gigya.get_person_id()
        return await self._request(
            "GET",
            f"/persons/{gigya_person_id}",
        )

    async def get_accounts(self) -> List[renault_account.RenaultAccount]:
        """Get list of accounts linked to credentials."""
        response_json = await self.get_accounts_raw()

        accounts = []
        for account_information in response_json.get("accounts", []):
            account_id = account_information["accountId"]
            accounts.append(renault_account.RenaultAccount(self, account_id))
        return accounts

    def get_account(self, account_id: str) -> renault_account.RenaultAccount:
        """Get list of accounts linked to credentials."""
        return renault_account.RenaultAccount(self, account_id)


def _raise_kamereon_errors(response_json: Any) -> None:
    pass
