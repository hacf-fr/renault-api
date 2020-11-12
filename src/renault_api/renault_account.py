"""Client for Renault API."""
from __future__ import annotations

import logging
from typing import Any

from . import renault_client


_LOGGER = logging.getLogger(__name__)


class RenaultAccount:
    """Proxy to a Renault account."""

    def __init__(
        self,
        client: renault_client.RenaultClient,
        account_id: str,
    ) -> None:
        """Initialise Renault account."""
        self._client = client
        self.account_id = account_id

    async def _request(self, method: str, path: str) -> Any:
        path = f"/accounts/{self.account_id}{path}"
        return await self._client._request(method, path)

    async def get_vehicles_raw(self) -> Any:
        """Get list of vehicles linked to Renault account."""
        return await self._request(
            "GET",
            "/vehicles",
        )
