"""Client for Renault API."""
from __future__ import annotations

import logging
from typing import List

from aiohttp import ClientSession

from . import renault_account


_LOGGER = logging.getLogger(__name__)


class RenaultClient:
    """Proxy to the Renault API."""

    def __init__(self, websession: ClientSession) -> None:
        """Initialise Renault Client."""
        self._websession = websession

    async def login(self, user: str, password: str) -> None:
        """Login."""
        pass

    async def get_accounts(self) -> List[renault_account.RenaultAccount]:
        """Get list of accounts linked to credentials."""
        return []

    async def get_account(self, account_id: str) -> renault_account.RenaultAccount:
        """Get list of accounts linked to credentials."""
        return renault_account.RenaultAccount(self, account_id)
