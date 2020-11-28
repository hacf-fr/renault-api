"""Client for Renault API."""
import logging
from typing import List

from . import kamereon
from .kamereon import models
from .renault_session import RenaultSession
from .renault_vehicle import RenaultVehicle


_LOGGER = logging.getLogger(__name__)


class RenaultAccount:
    """Proxy to a Renault account."""

    def __init__(
        self,
        session: RenaultSession,
        account_id: str,
    ) -> None:
        """Initialise Renault account."""
        self._session = session
        self._account_id = account_id

    @property
    def session(self) -> RenaultSession:
        """Get session provider."""
        return self._session

    @property
    def account_id(self) -> str:
        """Get account id."""
        return self._account_id

    async def get_vehicles(self) -> models.KamereonVehiclesResponse:
        """GET to /accounts/{account_id}/vehicles."""
        return await kamereon.get_vehicles(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self.account_id,
        )

    async def get_api_vehicles(self) -> List[RenaultVehicle]:
        """Get list of accounts linked to credentials."""
        response = await self.get_vehicles()
        return list(
            RenaultVehicle(self._session, self._account_id, vehicle.get_vin())
            for vehicle in response.vehicleLinks
        )

    async def get_api_vehicle(self, vin: str) -> RenaultVehicle:
        """Get list of accounts linked to credentials."""
        return RenaultVehicle(self._session, self._account_id, vin)
