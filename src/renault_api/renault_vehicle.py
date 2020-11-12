"""Client for Renault API."""
from __future__ import annotations

import logging

from . import renault_account


_LOGGER = logging.getLogger(__name__)


class RenaultVehicle:
    """Proxy to a Renault vehicle."""

    def __init__(
        self,
        account: renault_account.RenaultAccount,
        vin: str,
    ) -> None:
        """Initialise Renault account."""
        self._account = account
        self._vin = vin
