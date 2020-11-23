"""Client for Renault API."""
import logging

from .kamereon import Kamereon


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
