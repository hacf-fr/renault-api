"""Client for Renault API."""
from __future__ import annotations

import logging
from typing import Any

from . import renault_client
from . import renault_vehicle
from .pyze_override import KamereonOverride

_LOGGER = logging.getLogger(__name__)


class RenaultAccount:
    """Proxy to a Renault account."""

    def __init__(
        self,
        parent_client: renault_client.RenaultClient,
        account_id: str,
    ) -> None:
        """Initialise Renault account."""
        self._parent_client: renault_client.RenaultClient = parent_client
        self._kamereon: KamereonOverride = KamereonOverride(
            credentials=parent_client._credential_store,
            gigya=parent_client._gigya,
            country=parent_client._country,
        )
        self._kamereon.set_account_id(account_id)

    def get_vehicles(self) -> Any:
        """Get list of vehicles linked to Renault account."""
        return self._kamereon.get_vehicles()

    def get_vehicle(self, vin: str) -> renault_vehicle.RenaultVehicle:
        """Get vehicle linked to Renault account."""
        return renault_vehicle.RenaultVehicle(self, vin)
