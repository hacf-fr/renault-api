"""Kamereon client for interaction with Renault servers."""
import logging
from typing import Any
from typing import cast
from typing import Dict
from typing import Optional

import aiohttp
from marshmallow.schema import Schema

from renault_api import kamereon
from renault_api import gigya
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.credential_store import CredentialStore
from renault_api.gigya.exceptions import GigyaException
from . import models
from . import schemas
from renault_api.credential import Credential
from renault_api.credential import JWTCredential


_LOGGER = logging.getLogger(__name__)


class KamereonClient:
    """Kamereon client for interaction with Renault servers."""

    def __init__(
        self,
        websession: aiohttp.ClientSession,
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

    async def get_person(self) -> models.KamereonPersonResponse:
        """GET to /persons/{person_id}."""
        return await kamereon.get_person(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            await self._get_person_id(),
        )

    async def get_vehicles(self, account_id: str) -> models.KamereonVehiclesResponse:
        """GET to /accounts/{account_id}/vehicles."""
        return await kamereon.get_vehicles(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
        )

    async def get_vehicle_battery_status(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/battery-status."""
        return await kamereon.get_vehicle_battery_status_v2(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_location(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/location."""
        return await kamereon.get_vehicle_location(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_hvac_status(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/hvac-status."""
        return await kamereon.get_vehicle_hvac_status(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_charge_mode(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charge-mode."""
        return await kamereon.get_vehicle_charge_mode(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_cockpit(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/cockpit."""
        return await kamereon.get_vehicle_cockpit(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_lock_status(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/lock-status."""
        return await kamereon.get_vehicle_lock_status(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_charging_settings(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charging-settings."""
        return await kamereon.get_vehicle_charging_settings(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_notification_settings(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/notification-settings."""
        return await kamereon.get_vehicle_notification_settings(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
        )

    async def get_vehicle_charges(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charges."""
        return await kamereon.get_vehicle_charges(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            params,
        )

    async def get_vehicle_charge_history(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/charge-history."""
        return await kamereon.get_vehicle_charge_history(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            params,
        )

    async def get_vehicle_hvac_sessions(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/hvac-sessions."""
        return await kamereon.get_vehicle_hvac_sessions(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            params,
        )

    async def get_vehicle_hvac_history(
        self, account_id: str, vin: str, params: Dict[str, str]
    ) -> models.KamereonVehicleDataResponse:
        """GET to /cars/{vin}/hvac-history."""
        return await kamereon.get_vehicle_hvac_history(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            params,
        )

    async def set_vehicle_hvac_start(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> models.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/hvac-start."""
        return await kamereon.set_vehicle_hvac_start(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            attributes,
        )

    async def set_vehicle_charge_schedule(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> models.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/charge-schedule."""
        return await kamereon.set_vehicle_charge_schedule(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            attributes,
        )

    async def set_vehicle_charge_mode(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> models.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/charge-mode."""
        return await kamereon.set_vehicle_charge_mode(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            attributes,
        )

    async def set_vehicle_charging_start(
        self, account_id: str, vin: str, attributes: Dict[str, Any]
    ) -> models.KamereonVehicleDataResponse:
        """POST to /cars/{vin}/actions/charging-start."""
        return await kamereon.set_vehicle_charging_start(
            self._websession,
            self._root_url,
            self._api_key,
            await self._get_jwt(),
            self._country,
            account_id,
            vin,
            attributes,
        )

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
