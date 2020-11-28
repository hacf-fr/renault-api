"""Client for Renault API."""
import logging
from typing import List

from . import kamereon
from .kamereon import models
from .renault_account import RenaultAccount
from .renault_session import RenaultSession


_LOGGER = logging.getLogger(__name__)


class RenaultClient:
    """Proxy to a Renault profile."""

    def __init__(
        self,
        session: RenaultSession,
    ) -> None:
        """Initialise Renault client."""
        self._session = session

    @property
    def session(self) -> RenaultSession:
        """Get session provider."""
        return self._session

    async def get_person(self) -> models.KamereonPersonResponse:
        """GET to /persons/{person_id}."""
        return await kamereon.get_person(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            await self.session.get_person_id(),
        )

    async def get_api_accounts(self) -> List[RenaultAccount]:
        """Get list of accounts."""
        response = await self.get_person()
        return list(
            RenaultAccount(self._session, account.get_account_id())
            for account in response.accounts
        )

    async def get_api_account(self, account_id: str) -> RenaultAccount:
        """Get account."""
        return RenaultAccount(self._session, account_id)
