"""Client for Renault API."""
import logging
from typing import List
from typing import Optional

import aiohttp

from .const import AVAILABLE_LOCALES
from .exceptions import RenaultException
from .kamereon.client import KamereonClient
from .kamereon.models import KamereonPersonResponse
from .renault_account import RenaultAccount


_LOGGER = logging.getLogger(__name__)


class RenaultClient:
    """Proxy to a Renault profile."""

    def __init__(
        self,
        kamereon: Optional[KamereonClient] = None,
        websession: Optional[aiohttp.ClientSession] = None,
        locale: Optional[str] = None,
    ) -> None:
        """Initialise Renault client."""
        if kamereon:
            self._kamereon = kamereon
        else:
            if websession is None:  # pragma: no cover
                raise RenaultException(
                    "`websession` is required if kamereon is not provided."
                )
            if locale is None:  # pragma: no cover
                raise RenaultException(
                    "`locale` is required if kamereon is not provided."
                )
            self._kamereon = KamereonClient(
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
