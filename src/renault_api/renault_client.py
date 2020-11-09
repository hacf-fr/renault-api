"""Client for Renault API."""
import logging
from typing import Any

from pyze.api.credentials import BasicCredentialStore  # type: ignore
from pyze.api.gigya import Gigya  # type: ignore

from . import renault_account
from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .const import CONF_LOCALE
from .pyze_override import KamereonOverride

_LOGGER = logging.getLogger(__name__)


class RenaultClient:
    """Proxy to the Renault API."""

    def __init__(self, credential_store: BasicCredentialStore) -> None:
        """Initialise Renault Client."""
        for key in [
            CONF_LOCALE,
            CONF_GIGYA_APIKEY,
            CONF_GIGYA_URL,
            CONF_KAMEREON_APIKEY,
            CONF_KAMEREON_URL,
        ]:
            if key not in credential_store:
                raise KeyError(f"{key} was not found in credential store.")

        self._credential_store = credential_store

        self._country: str = self._credential_store[CONF_LOCALE][-2:]
        self._gigya: Gigya = Gigya(
            api_key=self._credential_store[CONF_GIGYA_APIKEY],
            credentials=self._credential_store,
            root_url=self._credential_store[CONF_GIGYA_URL],
        )
        self._kamereon: KamereonOverride = KamereonOverride(
            credentials=self._credential_store,
            gigya=self._gigya,
            country=self._country,
        )

    def login(self, user: str, password: str) -> Any:
        """Get API keys for specified locale and load into credential store."""
        login_result = self._gigya.login(user, password)
        self._gigya.account_info()
        return login_result

    def get_accounts(self) -> Any:
        """Get list of accounts linked to credentials."""
        return self._kamereon.get_accounts()

    def get_account(self, account_id: str) -> renault_account.RenaultAccount:
        """Get list of accounts linked to credentials."""
        return renault_account.RenaultAccount(self, account_id)
