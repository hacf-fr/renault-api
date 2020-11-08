"""Client for Renault API."""
from __future__ import annotations

import logging
from typing import Any
from typing import TYPE_CHECKING

from .pyze_override import KamereonOverride
from .renault_vehicle import RenaultVehicle

if TYPE_CHECKING:
    from .renault_client import RenaultClient

_LOGGER = logging.getLogger(__name__)


class RenaultAccount:
    """Proxy to a Renault account."""

    def __init__(
        self,
        renault_client: RenaultClient,
        account_id: str,
    ) -> None:
        """Initialise Renault account."""
        self._renault_client: RenaultClient = renault_client
        self._kamereon: KamereonOverride = KamereonOverride(
            credentials=renault_client._credential_store,
            gigya=renault_client._gigya,
            country=renault_client._country,
        )
        self._kamereon.set_account_id(account_id)

    def get_vehicles(self) -> Any:
        """Get list of vehicles linked to Renault account."""
        return self._kamereon.get_vehicles()

    def get_vehicle(self, vin: str) -> RenaultVehicle:
        """Get vehicle linked to Renault account."""
        return RenaultVehicle(self, vin)
