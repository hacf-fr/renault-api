"""Session provider for interaction with Renault servers."""
import logging
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp

from . import gigya
from . import kamereon
from .const import CONF_COUNTRY
from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .const import CONF_LOCALE
from .credential import Credential
from .credential import JWTCredential
from .credential_store import CredentialStore
from .exceptions import RenaultException
from .kamereon import models
from renault_api.helpers import get_api_keys


_LOGGER = logging.getLogger(__name__)


class RenaultSession:
    """Kamereon client for interaction with Renault servers."""

    def __init__(
        self,
        websession: aiohttp.ClientSession,
        locale: Optional[str] = None,
        country: Optional[str] = None,
        locale_details: Optional[Dict[str, str]] = None,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise SessionProvider."""
        self._websession = websession
        self._credentials: CredentialStore = credential_store or CredentialStore()

        if locale_details:
            for k, v in locale_details.items():
                self._credentials[k] = Credential(v)
        if locale:
            self._credentials[CONF_LOCALE] = Credential(locale)
        if country:
            self._credentials[CONF_COUNTRY] = Credential(country)

    async def login(self, login_id: str, password: str) -> None:
        """Forward login to Gigya."""
        self._credentials.clear_keys(gigya.GIGYA_KEYS)

        response = await gigya.login(
            self._websession,
            await self._get_gigya_root_url(),
            await self._get_gigya_api_key(),
            login_id,
            password,
        )
        credential = Credential(response.get_session_cookie())
        self._credentials[gigya.GIGYA_LOGIN_TOKEN] = credential

    async def _get_credential(self, key: str) -> str:
        if key not in self._credentials:
            if CONF_LOCALE in self._credentials:
                await self._update_from_locale()

        value = self._credentials.get_value(key)
        if value:
            return value
        raise RenaultException(f"Credential `{key}` not found in credential cache.")

    async def _update_from_locale(self) -> None:
        locale = await self._get_credential(CONF_LOCALE)
        if CONF_COUNTRY not in self._credentials:
            self._credentials[CONF_COUNTRY] = Credential(locale[-2:])
        locale_details = await get_api_keys(locale=locale, websession=self._websession)
        for k, v in locale_details.items():
            if k not in self._credentials:
                self._credentials[k] = Credential(v)

    async def _get_country(self) -> str:
        return await self._get_credential(CONF_COUNTRY)

    async def _get_kamereon_api_key(self) -> str:
        return await self._get_credential(CONF_KAMEREON_APIKEY)

    async def _get_kamereon_root_url(self) -> str:
        return await self._get_credential(CONF_KAMEREON_URL)

    async def _get_gigya_api_key(self) -> str:
        return await self._get_credential(CONF_GIGYA_APIKEY)

    async def _get_gigya_root_url(self) -> str:
        return await self._get_credential(CONF_GIGYA_URL)

    async def _get_login_token(self) -> str:
        return await self._get_credential(gigya.GIGYA_LOGIN_TOKEN)

    async def _get_person_id(self) -> str:
        """Get person id."""
        person_id = self._credentials.get_value(gigya.GIGYA_PERSON_ID)
        if person_id:
            return person_id
        login_token = await self._get_login_token()
        response = await gigya.get_account_info(
            self._websession,
            await self._get_gigya_root_url(),
            await self._get_gigya_api_key(),
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
        login_token = await self._get_login_token()
        response = await gigya.get_jwt(
            self._websession,
            await self._get_gigya_root_url(),
            await self._get_gigya_api_key(),
            login_token,
        )
        jwt = response.get_jwt()
        self._credentials[gigya.GIGYA_JWT] = JWTCredential(jwt)
        return jwt

    async def get_person(self) -> models.KamereonPersonResponse:
        """GET to /persons/{person_id}."""
        return await kamereon.get_person(
            websession=self._websession,
            root_url=await self._get_kamereon_root_url(),
            api_key=await self._get_kamereon_api_key(),
            gigya_jwt=await self._get_jwt(),
            country=await self._get_country(),
            person_id=await self._get_person_id(),
        )

    async def get_account_vehicles(
        self, account_id: str
    ) -> models.KamereonVehiclesResponse:
        """GET to /accounts/{account_id}/vehicles."""
        return await kamereon.get_account_vehicles(
            websession=self._websession,
            root_url=await self._get_kamereon_root_url(),
            api_key=await self._get_kamereon_api_key(),
            gigya_jwt=await self._get_jwt(),
            country=await self._get_country(),
            account_id=account_id,
        )

    async def get_vehicle_data(
        self,
        account_id: str,
        vin: str,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
    ) -> models.KamereonVehicleDataResponse:
        """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
        return await kamereon.get_vehicle_data(
            websession=self._websession,
            root_url=await self._get_kamereon_root_url(),
            api_key=await self._get_kamereon_api_key(),
            gigya_jwt=await self._get_jwt(),
            country=await self._get_country(),
            account_id=account_id,
            vin=vin,
            endpoint=endpoint,
            params=params,
        )

    async def set_vehicle_action(
        self,
        account_id: str,
        vin: str,
        endpoint: str,
        attributes: Dict[str, Any],
    ) -> models.KamereonVehicleDataResponse:
        """POST to /v{endpoint_version}/cars/{vin}/actions/{endpoint}."""
        return await kamereon.set_vehicle_action(
            websession=self._websession,
            root_url=await self._get_kamereon_root_url(),
            api_key=await self._get_kamereon_api_key(),
            gigya_jwt=await self._get_jwt(),
            country=await self._get_country(),
            account_id=account_id,
            vin=vin,
            endpoint=endpoint,
            attributes=attributes,
        )
