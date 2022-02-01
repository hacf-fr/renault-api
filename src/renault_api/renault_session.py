"""Session provider for interaction with Renault servers."""
import asyncio
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
from .exceptions import NotAuthenticatedException
from .exceptions import RenaultException
from .gigya.exceptions import GigyaResponseException
from .kamereon import models
from renault_api.helpers import get_api_keys


_LOGGER = logging.getLogger(__name__)


class RenaultSession:
    """Renault session for interaction with Renault servers."""

    def __init__(
        self,
        websession: aiohttp.ClientSession,
        locale: Optional[str] = None,
        country: Optional[str] = None,
        locale_details: Optional[Dict[str, str]] = None,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise RenaultSession."""
        self._gigya_lock = asyncio.Lock()
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
        """Attempt login on Gigya."""
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
        """Get specified credential, or raise RenaultException."""
        if key not in self._credentials:
            if CONF_LOCALE in self._credentials:
                await self._update_from_locale()

        value = self._credentials.get_value(key)
        if value:
            return value

        if key == gigya.GIGYA_LOGIN_TOKEN:
            raise NotAuthenticatedException("Gigya login token not available.")
        raise RenaultException(f"Credential `{key}` not found in credential cache.")

    async def _update_from_locale(self) -> None:
        """Update all missing setting based on locale."""
        locale = await self._get_credential(CONF_LOCALE)
        if CONF_COUNTRY not in self._credentials:
            self._credentials[CONF_COUNTRY] = Credential(locale[-2:])
        locale_details = await get_api_keys(locale=locale, websession=self._websession)
        for k, v in locale_details.items():
            if k not in self._credentials:
                self._credentials[k] = Credential(v)

    async def _get_country(self) -> str:
        """Get country from credential store."""
        return await self._get_credential(CONF_COUNTRY)

    async def _get_kamereon_api_key(self) -> str:
        """Get Kamereon api-key from credential store."""
        return await self._get_credential(CONF_KAMEREON_APIKEY)

    async def _get_kamereon_root_url(self) -> str:
        """Get Kamereon root url from credential store."""
        return await self._get_credential(CONF_KAMEREON_URL)

    async def _get_gigya_api_key(self) -> str:
        """Get Gigya api-key from credential store."""
        return await self._get_credential(CONF_GIGYA_APIKEY)

    async def _get_gigya_root_url(self) -> str:
        """Get Gigya root url from credential store."""
        return await self._get_credential(CONF_GIGYA_URL)

    async def _get_login_token(self) -> str:
        """Get current login token from credential store."""
        return await self._get_credential(gigya.GIGYA_LOGIN_TOKEN)

    async def _get_person_id(self) -> str:
        """Get person id from credential store or from Gigya."""
        async with self._gigya_lock:
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
        """Get json web token from credential store or from Gigya.."""
        async with self._gigya_lock:
            jwt = self._credentials.get_value(gigya.GIGYA_JWT)
            if jwt:
                return jwt
            login_token = await self._get_login_token()
            try:
                response = await gigya.get_jwt(
                    self._websession,
                    await self._get_gigya_root_url(),
                    await self._get_gigya_api_key(),
                    login_token,
                )
            except GigyaResponseException as exc:
                if exc.error_code in [403005, 403013]:  # pragma: no branch
                    self._credentials.clear_keys(gigya.GIGYA_KEYS)
                raise NotAuthenticatedException("Authentication expired.") from exc
            else:
                jwt = response.get_jwt()
                self._credentials[gigya.GIGYA_JWT] = JWTCredential(jwt)
                return jwt

    async def http_request(
        self, method: str, endpoint: str, json: Optional[Dict[str, Any]] = None
    ) -> models.KamereonResponse:
        """GET to specified endpoint."""
        url = (await self._get_kamereon_root_url()) + endpoint
        params = {"country": await self._get_country()}
        return await kamereon.request(
            websession=self._websession,
            method=method,
            url=url,
            api_key=await self._get_kamereon_api_key(),
            gigya_jwt=await self._get_jwt(),
            params=params,
            json=json,
        )

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

    async def get_vehicle_details(
        self, account_id: str, vin: str
    ) -> models.KamereonVehicleDetailsResponse:
        """GET to /accounts/{account_id}/vehicles/{vin}/details."""
        return await kamereon.get_vehicle_details(
            websession=self._websession,
            root_url=await self._get_kamereon_root_url(),
            api_key=await self._get_kamereon_api_key(),
            gigya_jwt=await self._get_jwt(),
            country=await self._get_country(),
            account_id=account_id,
            vin=vin,
        )

    async def get_vehicle_data(
        self,
        account_id: str,
        vin: str,
        endpoint: str,
        params: Optional[Dict[str, str]] = None,
        *,
        adapter_type: str = "kca",
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
            adapter_type=adapter_type,
        )

    async def get_vehicle_contracts(
        self,
        account_id: str,
        vin: str,
    ) -> models.KamereonVehicleContractsResponse:
        """GET to /v{endpoint_version}/cars/{vin}/contracts."""
        return await kamereon.get_vehicle_contracts(
            websession=self._websession,
            root_url=await self._get_kamereon_root_url(),
            api_key=await self._get_kamereon_api_key(),
            gigya_jwt=await self._get_jwt(),
            country=await self._get_country(),
            account_id=account_id,
            vin=vin,
            locale=await self._get_credential(CONF_LOCALE),
        )

    async def set_vehicle_action(
        self,
        account_id: str,
        vin: str,
        endpoint: str,
        attributes: Dict[str, Any],
        *,
        adapter_type: str = "kca",
    ) -> models.KamereonVehicleDataResponse:
        """POST to /v{endpoint_version}/cars/{vin}/{endpoint}."""
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
            adapter_type=adapter_type,
        )
