"""Client for Renault API."""
import logging
from typing import Dict
from typing import List
from typing import Optional

import aiohttp

from .credential_store import CredentialStore
from .exceptions import RenaultException
from .kamereon import models
from .renault_session import RenaultSession
from .renault_vehicle import RenaultVehicle


_LOGGER = logging.getLogger(__name__)


class RenaultAccount:
    """Proxy to a Renault account."""

    def __init__(
        self,
        account_id: str,
        session: Optional[RenaultSession] = None,
        websession: Optional[aiohttp.ClientSession] = None,
        locale: Optional[str] = None,
        country: Optional[str] = None,
        locale_details: Optional[Dict[str, str]] = None,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise Renault account."""
        self._account_id = account_id

        if session:
            self._session = session
        else:
            if websession is None:  # pragma: no cover
                raise RenaultException(
                    "`websession` is required if session is not provided."
                )
            self._session = RenaultSession(
                websession=websession,
                locale=locale,
                country=country,
                locale_details=locale_details,
                credential_store=credential_store,
            )

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
        return await self.session.get_account_vehicles(
            self.account_id,
        )

    async def get_api_vehicles(self) -> List[RenaultVehicle]:
        """Get vehicle proxies."""
        response = await self.get_vehicles()
        if response.vehicleLinks is None:  # pragma: no cover
            raise ValueError("response.accounts is None")
        result: List[RenaultVehicle] = []
        for vehicle in response.vehicleLinks:
            if vehicle.vin is None:  # pragma: no cover
                continue
            result.append(
                RenaultVehicle(
                    account_id=self.account_id,
                    vin=vehicle.vin,
                    session=self.session,
                    vehicle_details=vehicle.vehicleDetails,
                )
            )
        return result

    async def get_api_vehicle(self, vin: str) -> RenaultVehicle:
        """Get vehicle proxy for specified vin."""
        return RenaultVehicle(account_id=self.account_id, vin=vin, session=self.session)
