"""Client for Renault API."""
import logging
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
from pyze.api import BasicCredentialStore
from pyze.api import Gigya
from pyze.api import Kamereon

from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .const import CONF_LOCALE
from .helpers import get_api_keys
from renault_api.renault_account import RenaultAccount

_LOGGER = logging.getLogger(__package__)


class RenaultClient:
    """Proxy to the Renault API."""

    def __init__(
        self,
        credential_store: BasicCredentialStore = None,
    ) -> None:
        """Initialise Renault Client."""
        self._credential_store: BasicCredentialStore = (
            credential_store or BasicCredentialStore()
        )
        country = None
        if CONF_LOCALE in self._credential_store:
            country = self._credential_store[CONF_LOCALE][:2]
        self._gigya: Gigya = Gigya(credentials=self._credential_store)
        self._kamereon: Kamereon = Kamereon(
            credentials=self._credential_store, gigya=self._gigya, country=country
        )
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None

    def set_api_keys(self, api_keys: Dict[str, str]) -> None:
        """Load API keys into credential store."""
        for key in [
            CONF_GIGYA_APIKEY,
            CONF_GIGYA_URL,
            CONF_KAMEREON_APIKEY,
            CONF_KAMEREON_URL,
        ]:
            if key not in api_keys:
                _LOGGER.warn("Key %s not found in api_keys %s", key, api_keys)
            else:
                self._credential_store.store(key, api_keys[key], None)

    def set_locale(self, locale: str) -> None:
        """Load API keys into credential store."""
        self._credential_store.store(CONF_LOCALE, locale, None)

    async def preload_api_keys(self, force_load: bool = False) -> None:
        """Get API keys for specified locale and load into credential store.

        Equivalent to get_api_keys + set_api_keys.

        Args:
            force_load (bool): bypass internal AVAILABLE_LOCALES
        """
        api_keys = await get_api_keys(
            self._credential_store[CONF_LOCALE], self.aiohttp_session, force_load
        )
        self.set_api_keys(api_keys)

    def login(self, user: str, password: str) -> Any:
        """Get API keys for specified locale and load into credential store."""
        login_result = self._gigya.login(user, password)
        self._gigya.account_info()
        return login_result

    def get_accounts(self) -> Any:
        """Get list of accounts linked to credentials."""
        return self._kamereon.get_accounts()

    def get_account(self, account_id: str) -> Any:
        """Get list of accounts linked to credentials."""
        return RenaultAccount(self._kamereon, account_id)
