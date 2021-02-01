"""Client for Renault API."""
import logging
from typing import Dict
from typing import List
from typing import Optional

import aiohttp

from .credential_store import CredentialStore
from .exceptions import RenaultException
from .kamereon import models
from .renault_account import RenaultAccount
from .renault_session import RenaultSession


_LOGGER = logging.getLogger(__name__)


class RenaultClient:
    """Proxy to a Renault profile."""

    def __init__(
        self,
        session: Optional[RenaultSession] = None,
        websession: Optional[aiohttp.ClientSession] = None,
        locale: Optional[str] = None,
        country: Optional[str] = None,
        locale_details: Optional[Dict[str, str]] = None,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise Renault client."""
        if session:
            self._session = session
        else:
            if websession is None:  # pragma: no cover
                raise RenaultException(
                    "`websession` is required if session is not provided."
                )
            self._session = RenaultSession(
                websession=websession,
                locale=locale,
                country=country,
                locale_details=locale_details,
                credential_store=credential_store,
            )

    @property
    def session(self) -> RenaultSession:
        """Get session provider."""
        return self._session

    async def get_person(self) -> models.KamereonPersonResponse:
        """GET to /persons/{person_id}."""
        return await self.session.get_person()

    async def get_api_accounts(self) -> List[RenaultAccount]:
        """Get account proxies."""
        response = await self.get_person()
        if response.accounts is None:  # pragma: no cover
            raise ValueError("response.accounts is None")
        result: List[RenaultAccount] = []
        for account in response.accounts:
            if account.accountId is None:  # pragma: no cover
                continue
            result.append(
                RenaultAccount(account_id=account.accountId, session=self.session)
            )
        return result

    async def get_api_account(self, account_id: str) -> RenaultAccount:
        """Get account proxy for specified account id."""
        return RenaultAccount(account_id=account_id, session=self.session)
