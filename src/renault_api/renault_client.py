"""Client for Renault API."""
import logging
from typing import List

from aiohttp import ClientSession

from .kamereon import Kamereon
from .renault_account import RenaultAccount
from renault_api.const import AVAILABLE_LOCALES
from renault_api.model.kamereon import KamereonPersonResponse


_LOGGER = logging.getLogger(__name__)


class RenaultClient:
    """Proxy to a Renault profile."""

    def __init__(self, websession: ClientSession, locale: str) -> None:
        """Initialise Renault client."""
        self._kamereon = Kamereon(
            websession=websession,
            country=locale[-2:],
            locale_details=AVAILABLE_LOCALES[locale],
        )

    async def login(self, login_id: str, password: str) -> None:
        """Login."""
        await self._kamereon.login(login_id, password)

    async def get_person(self) -> KamereonPersonResponse:
        """Get person details."""
        return await self._kamereon.get_person()

    async def get_api_accounts(self) -> List[RenaultAccount]:
        """Get list of accounts."""
        response = await self.get_person()
        return list(
            RenaultAccount(self._kamereon, account.get_account_id())
            for account in response.accounts
        )

    async def get_api_account(self, account_id: str) -> RenaultAccount:
        """Get account."""
        return RenaultAccount(self._kamereon, account_id)
