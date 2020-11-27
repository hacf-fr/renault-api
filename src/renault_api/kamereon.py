"""Kamereon client for interaction with Renault servers."""
import logging
from typing import Any
from typing import cast
from typing import Dict
from typing import Optional

from aiohttp import ClientSession
from marshmallow.schema import Schema

from . import gigya
from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .credential_store import CredentialStore
from .gigya.exceptions import GigyaException
from .model import kamereon as model
from .model.credential import Credential
from .model.credential import JWTCredential


_LOGGER = logging.getLogger(__name__)


class Kamereon:
    """Kamereon client for interaction with Renault servers."""

    def __init__(
        self,
        websession: ClientSession,
        country: str,
        locale_details: Dict[str, str],
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise Kamereon."""
        self._websession = websession

        self._country = country
        self._api_key = locale_details[CONF_KAMEREON_APIKEY]
        self._root_url = locale_details[CONF_KAMEREON_URL]
        self._gigya_api_key = locale_details[CONF_GIGYA_APIKEY]
        self._gigya_root_url = locale_details[CONF_GIGYA_URL]
        self._credentials: CredentialStore = credential_store or CredentialStore()

    def _get_path_to_account(self, account_id: str) -> str:
        """Get the path to the account."""
        return f"/accounts/{account_id}"

    def _get_path_to_car(self, account_id: str, version: int, vin: str) -> str:
        """Get the path to the car."""
        account_path = self._get_path_to_account(account_id)
        return f"{account_path}/kamereon/kca/car-adapter/v{version}/cars/{vin}"

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
            "x-gigya-id_token": await self._get_jwt(),
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
        """Forward login to Gigya."""
        self._credentials.clear_keys(gigya.GIGYA_KEYS)

        response = await gigya.login(
            self._websession,
            self._gigya_root_url,
            self._gigya_api_key,
            login_id,
            password,
        )
        credential = Credential(response.get_session_cookie())
        self._credentials[gigya.GIGYA_LOGIN_TOKEN] = credential

    async def get_person(self) -> model.KamereonPersonResponse:
        """GET to /persons/{person_id}."""
        person_id = await self._get_person_id()
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
    ) -> model.KamereonVehicleDataResponse:
        """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
        path_to_car = self._get_path_to_car(account_id, endpoint_version, vin)
        return cast(
            model.KamereonVehicleDataResponse,
            await self._request(
                schema=model.KamereonVehicleDataResponseSchema,
                method="GET",
                path=f"{path_to_car}/{endpoint}",
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

    async def set_vehicle_data(
        self,
        account_id: str,
        endpoint_version: int,
        vin: str,
        endpoint: str,
        data: Dict[str, Any],
    ) -> model.KamereonVehicleDataResponse:
        """POST to /v{endpoint_version}/cars/{vin}/actions/{endpoint}."""
        path_to_car = self._get_path_to_car(account_id, endpoint_version, vin)
        return cast(
            model.KamereonVehicleDataResponse,
            await self._request(
                schema=model.KamereonVehicleDataResponseSchema,
                method="POST",
                path=f"{path_to_car}/actions/{endpoint}",
                data=data,
            ),
        )

    async def set_vehicle_hvac_start(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> model.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/hvac-start."""
        data = {"type": "HvacStart", "attributes": attributes}
        return await self.set_vehicle_data(account_id, 1, vin, "hvac-start", data)

    async def set_vehicle_charge_schedule(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> model.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/charge-schedule."""
        data = {"type": "ChargeSchedule", "attributes": attributes}
        return await self.set_vehicle_data(account_id, 2, vin, "charge-schedule", data)

    async def set_vehicle_charge_mode(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> model.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/charge-mode."""
        data = {"type": "ChargeMode", "attributes": attributes}
        return await self.set_vehicle_data(account_id, 1, vin, "charge-mode", data)

    async def set_vehicle_charging_start(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> model.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/charging-start."""
        data = {"type": "ChargingStart", "attributes": attributes}
        return await self.set_vehicle_data(account_id, 1, vin, "charging-start", data)

    def _get_login_token(self) -> str:
        login_token = self._credentials.get_value(gigya.GIGYA_LOGIN_TOKEN)
        if login_token:
            return login_token
        raise GigyaException(
            f"Credential `{gigya.GIGYA_LOGIN_TOKEN}` not found in credential cache."
        )

    async def _get_person_id(self) -> str:
        """Get person id."""
        person_id = self._credentials.get_value(gigya.GIGYA_PERSON_ID)
        if person_id:
            return person_id
        login_token = self._get_login_token()
        response = await gigya.get_account_info(
            self._websession,
            self._gigya_root_url,
            self._gigya_api_key,
            login_token,
        )
        person_id = response.get_person_id()
        self._credentials[gigya.GIGYA_PERSON_ID] = Credential(person_id)
        return person_id

    async def _get_jwt(self) -> str:
        """Get json web token."""
        jwt = self._credentials.get_value(gigya.GIGYA_JWT)
        if jwt:
            return jwt
        login_token = self._get_login_token()
        response = await gigya.get_jwt(
            self._websession,
            self._gigya_root_url,
            self._gigya_api_key,
            login_token,
        )
        jwt = response.get_jwt()
        self._credentials[gigya.GIGYA_JWT] = JWTCredential(jwt)
        return jwt
