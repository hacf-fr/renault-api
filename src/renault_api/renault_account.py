"""Client for Renault API."""

import logging

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
        session: RenaultSession | None = None,
        websession: aiohttp.ClientSession | None = None,
        locale: str | None = None,
        country: str | None = None,
        locale_details: dict[str, str] | None = None,
        credential_store: CredentialStore | None = None,
    ) -> None:
        """Initialise Renault account."""
        self._account_id = account_id

        if session:
            self._session = session
        else:
            if websession is None:
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

    async def get_api_vehicles(self) -> list[RenaultVehicle]:
        """Get vehicle proxies."""
        response = await self.get_vehicles()
        if response.vehicleLinks is None:
            raise ValueError("response.accounts is None")
        result: list[RenaultVehicle] = []
        for vehicle in response.vehicleLinks:
            if vehicle.vin is None:
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
