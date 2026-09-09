"""Session provider for interaction with Renault servers."""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import aiohttp
from marshmallow.schema import Schema

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


@dataclass
class _PendingTwoFactorAuth:
    """State needed to complete an in-progress email TFA challenge."""

    reg_token: str
    gigya_assertion: str
    phv_token: str


class RenaultSession:
    """Renault session for interaction with Renault servers."""

    def __init__(
        self,
        websession: aiohttp.ClientSession,
        locale: str | None = None,
        country: str | None = None,
        locale_details: dict[str, str] | None = None,
        credential_store: CredentialStore | None = None,
    ) -> None:
        """Initialise RenaultSession."""
        self._gigya_lock = asyncio.Lock()
        self._websession = websession
        self._credentials: CredentialStore = credential_store or CredentialStore()
        self._pending_login: tuple[str, str] | None = None
        self._tfa: _PendingTwoFactorAuth | None = None

        if locale_details:
            for k, v in locale_details.items():
                self._credentials[k] = Credential(v)
        if locale:
            self._credentials[CONF_LOCALE] = Credential(locale)
        if country:
            self._credentials[CONF_COUNTRY] = Credential(country)

    async def login(self, login_id: str, password: str) -> None:
        """Attempt login on Gigya.

        Raises `PendingTwoFactorAuthenticationException` if the account
        requires two-factor authentication (see
        https://github.com/hacf-fr/renault-api/issues/2132). Catch it, then
        call `request_two_factor_auth_code` followed by
        `complete_two_factor_auth` (which calls back into `login`) to finish.
        """
        self._credentials.clear_keys(gigya.GIGYA_KEYS)
        # Kept in memory (never persisted) so `complete_two_factor_auth` can
        # replay the login once the pending TFA challenge is resolved.
        self._pending_login = (login_id, password)

        response = await gigya.login(
            self._websession,
            await self._get_gigya_root_url(),
            await self._get_gigya_api_key(),
            login_id,
            password,
        )
        credential = Credential(response.get_session_cookie())
        self._credentials[gigya.GIGYA_LOGIN_TOKEN] = credential
        self._pending_login = None

    async def request_two_factor_auth_code(self, reg_token: str) -> None:
        """Start an email one-time-code two-factor authentication challenge.

        `reg_token` comes from `PendingTwoFactorAuthenticationException.reg_token`,
        raised by `login`. This emails a one-time code to the account's
        registered address; pass it to `complete_two_factor_auth` once known.
        Currently only the email one-time-code method is supported.
        """
        root_url = await self._get_gigya_root_url()
        api_key = await self._get_gigya_api_key()

        init_response = await gigya.init_tfa(
            self._websession, root_url, api_key, reg_token
        )
        gigya_assertion = init_response.get_gigya_assertion()

        emails_response = await gigya.get_tfa_emails(
            self._websession, root_url, api_key, gigya_assertion
        )
        email_id = emails_response.get_email_id()

        send_response = await gigya.send_tfa_email_code(
            self._websession, root_url, api_key, gigya_assertion, email_id
        )
        self._tfa = _PendingTwoFactorAuth(
            reg_token=reg_token,
            gigya_assertion=gigya_assertion,
            phv_token=send_response.get_phv_token(),
        )

    async def complete_two_factor_auth(
        self, code: str, *, remember_device: bool = True
    ) -> None:
        """Submit the emailed one-time code and finish logging in.

        Must be called after `request_two_factor_auth_code`, on the same
        `RenaultSession` that raised `PendingTwoFactorAuthenticationException`.
        When `remember_device` is True (the default), Gigya should not
        require another TFA challenge on this session for about 30 days.
        """
        if not self._tfa:
            raise RenaultException(
                "No two-factor authentication challenge is pending; "
                "call `request_two_factor_auth_code` first."
            )
        if not self._pending_login:
            raise RenaultException(
                "`login` must be called before completing two-factor authentication."
            )
        tfa = self._tfa
        root_url = await self._get_gigya_root_url()
        api_key = await self._get_gigya_api_key()

        complete_response = await gigya.complete_tfa_email_verification(
            self._websession,
            root_url,
            api_key,
            tfa.gigya_assertion,
            tfa.phv_token,
            code,
        )
        await gigya.finalize_tfa(
            self._websession,
            root_url,
            api_key,
            tfa.gigya_assertion,
            complete_response.get_provider_assertion(),
            tfa.reg_token,
            remember_device=remember_device,
        )
        # The challenge is now resolved (the code is single-use) - clear it
        # even if the re-login below fails, so a retry doesn't replay it.
        self._tfa = None
        login_id, password = self._pending_login
        await self.login(login_id, password)

    @property
    def login_token(self) -> str | None:
        """Return the current Gigya login token.

        This token is obtained from the password on `login`, and is used to
        mint JWTs (access tokens) without re-supplying the password. Store it
        securely instead of the password, and restore it with `set_login_token`
        (or by pre-populating the credential store) on the next session.
        """
        return self._credentials.get_value(gigya.GIGYA_LOGIN_TOKEN)

    def set_login_token(self, login_token: str) -> None:
        """Restore a Gigya login token obtained from a previous session.

        This avoids storing and reusing the user password: a session restored
        this way can mint JWTs without ever calling `login`.
        """
        self._credentials.clear_keys(gigya.GIGYA_KEYS)
        self._credentials[gigya.GIGYA_LOGIN_TOKEN] = Credential(login_token)

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
                if exc.error_code in [403005, 403013]:
                    self._credentials.clear_keys(gigya.GIGYA_KEYS)
                raise NotAuthenticatedException("Authentication expired.") from exc
            else:
                jwt = response.get_jwt()
                self._credentials[gigya.GIGYA_JWT] = JWTCredential(jwt)
                return jwt

    async def http_request(
        self,
        method: str,
        endpoint: str,
        json: dict[str, Any] | None = None,
        *,
        schema: Schema | None = None,
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
            schema=schema,
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
        params: dict[str, str] | None = None,
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
        attributes: dict[str, Any],
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
