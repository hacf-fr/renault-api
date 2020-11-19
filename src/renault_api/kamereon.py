"""Kamereon client for interaction with Renault servers."""
import logging
from typing import Any
from typing import cast
from typing import Dict
from typing import Optional

from aiohttp import ClientSession
from marshmallow.schema import Schema

from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .exceptions import KamereonException
from .gigya import Gigya
from renault_api.model import kamereon as model
from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential

CREDENTIAL_GIGYA_JWT = "gigya_jwt"
CREDENTIAL_GIGYA_LOGIN_TOKEN = "gigya_login_token"
CREDENTIAL_GIGYA_PERSON_ID = "gigya_person_id"

_LOGGER = logging.getLogger(__name__)


class Kamereon(object):
    """Kamereon client for interaction with Renault servers."""

    def __init__(
        self,
        websession: ClientSession,
        country: str,
        locale_details: Dict[str, str],
        gigya: Optional[Gigya] = None,
    ) -> None:
        """Initialise Kamereon."""
        self._websession = websession

        self._country = country
        self._api_key = locale_details[CONF_KAMEREON_APIKEY]
        self._root_url = locale_details[CONF_KAMEREON_URL]

        self._gigya = gigya or Gigya(
            websession=websession, locale_details=locale_details
        )
        self._credentials: Dict[str, Credential] = {}

    async def _get_credential(self, key: str) -> str:
        credential = self._credentials.get(key)
        if credential and not credential.has_expired():
            return credential.value

        if key == CREDENTIAL_GIGYA_JWT:
            login_token = await self._get_credential(CREDENTIAL_GIGYA_LOGIN_TOKEN)
            jwt_response = await self._gigya.get_jwt(login_token)
            credential = JWTCredential(jwt_response.get_jwt_token())
            self._credentials[key] = credential
            return credential.value
        if key == CREDENTIAL_GIGYA_PERSON_ID:
            login_token = await self._get_credential(CREDENTIAL_GIGYA_LOGIN_TOKEN)
            account_response = await self._gigya.get_account_info(login_token)
            credential = Credential(account_response.get_person_id())
            self._credentials[key] = credential
            return credential.value

        raise KamereonException(f"Credential `{key}` not found in credential cache.")

    def _get_car_adapter_path(self, account_id: str) -> str:
        """Get the car-adapter /cars/{vin}/battery-status."""
        return f"/accounts/{account_id}/kamereon/kca/car-adapter"

    async def _request(
        self,
        schema: Schema,
        method: str,
        path: str,
        params: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> model.KamereonResponse:
        url = f"{self._root_url}/commerce/v1{path}"
        headers = {
            "apikey": self._api_key,
            "x-gigya-id_token": await self._get_credential(CREDENTIAL_GIGYA_JWT),
        }
        params = params or {}
        params["country"] = self._country

        async with self._websession.request(
            method,
            url,
            headers=headers,
            params=params,
            data=data,
        ) as http_response:
            response_text = await http_response.text()
            _LOGGER.debug(
                "Received Kamereon response %s on %s: %s",
                http_response.status,
                http_response.url,
                response_text,
            )
            kamereon_response: model.KamereonResponse = schema.loads(response_text)
            # Check for Kamereon error
            kamereon_response.raise_for_error_code()
            # Check for HTTP error
            http_response.raise_for_status()

            return kamereon_response

    async def login(self, login_id: str, password: str) -> None:
        """Forward login to Gigya, and cache the login token."""
        self._credentials.clear()
        response = await self._gigya.login(login_id, password)
        self._credentials[CREDENTIAL_GIGYA_LOGIN_TOKEN] = Credential(
            response.get_session_cookie()
        )

    async def get_person(self) -> model.KamereonPersonResponse:
        """GET to /persons/{person_id}."""
        person_id = await self._get_credential(CREDENTIAL_GIGYA_PERSON_ID)
        return cast(
            model.KamereonPersonResponse,
            await self._request(
                schema=model.KamereonPersonResponseSchema,
                method="GET",
                path=f"/persons/{person_id}",
            ),
        )

    async def get_vehicles(self, account_id: str) -> model.KamereonVehiclesResponse:
        """GET to /accounts/{account_id}/vehicles."""
        return cast(
            model.KamereonVehiclesResponse,
            await self._request(
                schema=model.KamereonVehiclesResponseSchema,
                method="GET",
                path=f"/accounts/{account_id}/vehicles",
            ),
        )

    async def get_vehicle_data(
        self,
        account_id: str,
        endpoint_version: int,
        vin: str,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        schema: Optional[Schema] = None,
    ) -> model.KamereonVehicleDataResponse:
        """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
        car_adapter_path = self._get_car_adapter_path(account_id)
        return cast(
            model.KamereonVehicleDataResponse,
            await self._request(
                schema=schema or model.KamereonVehicleDataResponseSchema,
                method="GET",
                path=f"{car_adapter_path}/v{endpoint_version}/cars/{vin}/{endpoint}",
                params=params,
            ),
        )

    async def get_vehicle_battery_status(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/battery-status."""
        return await self.get_vehicle_data(account_id, 2, vin, "battery-status")

    async def get_vehicle_location(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/location."""
        return await self.get_vehicle_data(account_id, 1, vin, "location")

    async def get_vehicle_hvac_status(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/hvac-status."""
        return await self.get_vehicle_data(account_id, 1, vin, "hvac-status")

    async def get_vehicle_charge_mode(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charge-mode."""
        return await self.get_vehicle_data(account_id, 1, vin, "charge-mode")

    async def get_vehicle_cockpit(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/cockpit."""
        return await self.get_vehicle_data(account_id, 2, vin, "cockpit")

    async def get_vehicle_lock_status(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/lock-status."""
        return await self.get_vehicle_data(account_id, 1, vin, "lock-status")

    async def get_vehicle_charging_settings(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charging-settings."""
        return await self.get_vehicle_data(account_id, 1, vin, "charging-settings")

    async def get_vehicle_notification_settings(
        self, account_id: str, vin: str
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/notification-settings."""
        return await self.get_vehicle_data(account_id, 1, vin, "notification-settings")

    async def get_vehicle_charges(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charges."""
        return await self.get_vehicle_data(account_id, 1, vin, "charges", params)

    async def get_vehicle_charge_history(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charge-history."""
        return await self.get_vehicle_data(account_id, 1, vin, "charge-history", params)

    async def get_vehicle_hvac_sessions(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/hvac-sessions."""
        return await self.get_vehicle_data(account_id, 1, vin, "hvac-sessions", params)

    async def get_vehicle_hvac_history(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> model.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/hvac-history."""
        return await self.get_vehicle_data(account_id, 1, vin, "hvac-history", params)
