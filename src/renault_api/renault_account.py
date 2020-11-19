"""Client for Renault API."""
import logging
from typing import List

from .kamereon import Kamereon
from .renault_vehicle import RenaultVehicle
from renault_api.model.kamereon import KamereonVehiclesResponse


_LOGGER = logging.getLogger(__name__)


class RenaultAccount:
    """Proxy to a Renault account."""

    def __init__(
        self,
        kamereon: Kamereon,
        account_id: str,
    ) -> None:
        """Initialise Renault account."""
        self._kamereon = kamereon
        self._account_id = account_id

    async def get_vehicles(self) -> KamereonVehiclesResponse:
        """Get vehicles."""
        return await self._kamereon.get_vehicles(self._account_id)

    async def get_api_vehicles(self) -> List[RenaultVehicle]:
        """Get list of accounts linked to credentials."""
        response = await self.get_vehicles()
        return list(
            RenaultVehicle(self._kamereon, self._account_id, vehicle.get_vin())
            for vehicle in response.vehicleLinks
        )

    async def get_api_vehicle(self, vin: str) -> RenaultVehicle:
        """Get list of accounts linked to credentials."""
        return RenaultVehicle(self._kamereon, self._account_id, vin)
