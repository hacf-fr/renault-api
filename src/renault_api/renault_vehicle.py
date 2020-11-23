"""Client for Renault API."""
import logging

from .kamereon import Kamereon
from .model.kamereon import KamereonVehicleBatteryStatusData
from .model.kamereon import KamereonVehicleBatteryStatusDataSchema
from .model.kamereon import KamereonVehicleHvacStatusData
from .model.kamereon import KamereonVehicleHvacStatusDataSchema


_LOGGER = logging.getLogger(__name__)


class RenaultVehicle:
    """Proxy to a Renault vehicle."""

    def __init__(
        self,
        kamereon: Kamereon,
        account_id: str,
        vin: str,
    ) -> None:
        """Initialise Renault account."""
        self._kamereon = kamereon
        self._account_id = account_id
        self._vin = vin

    async def get_battery_status(self) -> KamereonVehicleBatteryStatusData:
        """Get vehicles."""
        response = await self._kamereon.get_vehicle_battery_status(
            self._account_id, self._vin
        )
        return response.get_attributes(KamereonVehicleBatteryStatusDataSchema)

    async def get_hvac_status(self) -> KamereonVehicleHvacStatusData:
        """Get vehicles."""
        response = await self._kamereon.get_vehicle_hvac_status(
            self._account_id, self._vin
        )
        return response.get_attributes(KamereonVehicleHvacStatusDataSchema)
