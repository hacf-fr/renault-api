"""Client for Renault API."""
import logging
from typing import Dict

from pyze.api import Kamereon
from pyze.api.kamereon import Vehicle

_LOGGER = logging.getLogger(__package__)


class RenaultVehicle:
    """Proxy to a Renault vehicle."""

    def __init__(self, kamereon: Kamereon, vin: str) -> None:
        """Initialise Renault vehicle."""
        self._vehicle: Vehicle = Vehicle(vin, kamereon)

    def battery_status(self) -> Dict:
        """Get vehicle battery status."""
        return self._vehicle.battery_status()
