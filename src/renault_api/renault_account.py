"""Client for Renault API."""
import copy
import logging
from typing import Any

from pyze.api import Kamereon  # type: ignore

from renault_api.renault_vehicle import RenaultVehicle


_LOGGER = logging.getLogger(__package__)


class RenaultAccount:
    """Proxy to a Renault account."""

    def __init__(self, kamereon: Kamereon, account_id: str) -> None:
        """Initialise Renault account."""
        self._kamereon: Kamereon = copy.deepcopy(kamereon)
        self._kamereon.set_account_id(account_id)

    def get_vehicles(self) -> Any:
        """Get list of vehicles linked to Renault account."""
        return self._kamereon.get_vehicles()

    def get_vehicle(self, vin: str) -> Any:
        """Get vehicle linked to Renault account."""
        return RenaultVehicle(self._kamereon, vin)
