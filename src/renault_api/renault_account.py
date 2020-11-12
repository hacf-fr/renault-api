"""Client for Renault API."""
from __future__ import annotations

import logging
from typing import List

from . import renault_client
from . import renault_vehicle


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
        self._account_id = account_id

    async def get_vehicles(self) -> List[renault_vehicle.RenaultVehicle]:
        """Get list of accounts linked to credentials."""
        return []

    async def get_vehicle(self, vin: str) -> renault_vehicle.RenaultVehicle:
        """Get list of accounts linked to credentials."""
        return renault_vehicle.RenaultVehicle(self, vin)
