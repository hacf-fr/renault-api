"""Session provider for interaction with Renault servers."""

import asyncio
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from dataclasses import field
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
from .gigya.exceptions import PendingTwoFactorAuthenticationException
from .gigya.models import GigyaTfaEmail
from .kamereon import models
from renault_api.helpers import get_api_keys

_LOGGER = logging.getLogger(__name__)


@dataclass
class _PendingTwoFactorAuth:
    """State needed to complete an in-progress email TFA challenge.

    Kept in memory only (never persisted): the credentials are needed to
    replay `login` once the challenge is resolved.
    """

    login_id: str
    password: str = field(repr=False)
    reg_token: str = field(repr=False)
    gigya_assertion: str | None = field(default=None, repr=False)
    phv_token: str | None = field(default=None, repr=False)


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
        self._pending_tfa: _PendingTwoFactorAuth | None = None

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
        requires two-factor authentication. In that case, send a one-time
        code with `request_two_factor_auth_code` (after letting the user pick
        an address from `get_two_factor_auth_emails` if there are several),
        then pass the code to `complete_two_factor_auth`.
        """
        self._credentials.clear_keys(gigya.GIGYA_KEYS)
        self._pending_tfa = None

        try:
            response = await gigya.login(
                self._websession,
                await self._get_gigya_root_url(),
                await self._get_gigya_api_key(),
                login_id=login_id,
                password=password,
                device_ids=self.device_ids or None,
            )
        except PendingTwoFactorAuthenticationException as exc:
            self._pending_tfa = _PendingTwoFactorAuth(
                login_id=login_id, password=password, reg_token=exc.reg_token
            )
            raise
        credential = Credential(response.get_session_cookie())
        self._credentials[gigya.GIGYA_LOGIN_TOKEN] = credential

    async def get_two_factor_auth_emails(self) -> list[GigyaTfaEmail]:
        """Return the email addresses registered for two-factor authentication.

        Each entry has an `id` (to pass to `request_two_factor_auth_code`) and
        an `obfuscated` address (eg. `e***@example.com`) to show to the user.
        """
        pending_tfa = self._get_pending_tfa()
        response = await gigya.get_tfa_emails(
            self._websession,
            await self._get_gigya_root_url(),
            await self._get_gigya_api_key(),
            device_ids=await self._get_device_ids(),
            gigya_assertion=await self._get_tfa_assertion(pending_tfa),
        )
        return [email for email in response.emails or [] if email.id]

    async def request_two_factor_auth_code(self, email_id: str | None = None) -> None:
        """Email a one-time code for the pending two-factor authentication.

        `email_id` is required if several addresses are registered (see
        `get_two_factor_auth_emails`), and defaults to the only one otherwise.
        """
        pending_tfa = self._get_pending_tfa()
        if email_id is None:
            email_ids = [
                email.id
                for email in await self.get_two_factor_auth_emails()
                if email.id
            ]
            if not email_ids:
                raise RenaultException(
                    "No email address is registered for two-factor authentication."
                )
            if len(email_ids) > 1:
                raise RenaultException(
                    "Several email addresses are registered for two-factor "
                    "authentication; `email_id` is required."
                )
            email_id = email_ids[0]

        response = await gigya.send_tfa_email_code(
            self._websession,
            await self._get_gigya_root_url(),
            await self._get_gigya_api_key(),
            device_ids=await self._get_device_ids(),
            gigya_assertion=await self._get_tfa_assertion(pending_tfa),
            email_id=email_id,
            lang=self._get_tfa_lang(),
        )
        pending_tfa.phv_token = response.get_phv_token()

    async def complete_two_factor_auth(
        self, code: str, *, remember_device: bool = True
    ) -> None:
        """Submit the emailed one-time code and finish logging in.

        Raises `InvalidVerificationCodeException` if the code is wrong. The
        challenge stays pending, so this can be called again with the right
        code, without requesting a new one.

        When `remember_device` is True (the default), Gigya should not ask
        for another code for this device for about 30 days. The device is
        identified by `device_ids`, which are sent explicitly with each
        request (so the aiohttp session may be shared): persist them with
        `device_ids`, and restore them with `set_device_ids`.
        """
        pending_tfa = self._get_pending_tfa()
        if not pending_tfa.gigya_assertion or not pending_tfa.phv_token:
            raise RenaultException(
                "No two-factor authentication code was requested; "
                "call `request_two_factor_auth_code` first."
            )
        root_url = await self._get_gigya_root_url()
        api_key = await self._get_gigya_api_key()
        device_ids = await self._get_device_ids()

        response = await gigya.complete_tfa_email_verification(
            self._websession,
            root_url,
            api_key,
            device_ids=device_ids,
            gigya_assertion=pending_tfa.gigya_assertion,
            phv_token=pending_tfa.phv_token,
            code=code,
        )
        await gigya.finalize_tfa(
            self._websession,
            root_url,
            api_key,
            device_ids=device_ids,
            gigya_assertion=pending_tfa.gigya_assertion,
            provider_assertion=response.get_provider_assertion(),
            reg_token=pending_tfa.reg_token,
            remember_device=remember_device,
        )
        await self.login(pending_tfa.login_id, pending_tfa.password)

    def _get_pending_tfa(self) -> _PendingTwoFactorAuth:
        """Get the pending two-factor authentication, or raise RenaultException."""
        if not self._pending_tfa:
            raise RenaultException(
                "No two-factor authentication is pending; call `login` first."
            )
        return self._pending_tfa

    async def _get_tfa_assertion(self, pending_tfa: _PendingTwoFactorAuth) -> str:
        """Get the assertion for the pending TFA, starting the challenge if needed."""
        if not pending_tfa.gigya_assertion:
            response = await gigya.init_tfa(
                self._websession,
                await self._get_gigya_root_url(),
                await self._get_gigya_api_key(),
                device_ids=await self._get_device_ids(),
                reg_token=pending_tfa.reg_token,
            )
            pending_tfa.gigya_assertion = response.get_gigya_assertion()
        return pending_tfa.gigya_assertion

    async def _get_device_ids(self) -> dict[str, str]:
        """Get the Gigya device identifiers, requesting new ones if needed."""
        if not (device_ids := self.device_ids):
            device_ids = await gigya.get_device_ids(
                self._websession,
                await self._get_gigya_root_url(),
                await self._get_gigya_api_key(),
            )
            self.set_device_ids(device_ids)
        return device_ids

    def _get_tfa_lang(self) -> str | None:
        """Get the language for two-factor authentication emails, from the locale."""
        if locale := self._credentials.get_value(CONF_LOCALE):
            return locale.split("_")[0]
        return None

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

    @property
    def device_ids(self) -> dict[str, str]:
        """Return the Gigya device identifiers (`gmid`/`ucid`).

        They are obtained during two-factor authentication, and identify the
        device that Gigya remembers afterwards. Store them alongside the login
        token, and restore them with `set_device_ids` on the next session, so
        that a later `login` doesn't require another two-factor challenge.
        """
        return {
            name: value
            for key, name in gigya.GIGYA_DEVICE_ID_KEYS.items()
            if (value := self._credentials.get_value(key))
        }

    def set_device_ids(self, device_ids: Mapping[str, str]) -> None:
        """Restore the Gigya device identifiers obtained from a previous session."""
        self._credentials.clear_keys(list(gigya.GIGYA_DEVICE_ID_KEYS))
        for key, name in gigya.GIGYA_DEVICE_ID_KEYS.items():
            if value := device_ids.get(name):
                self._credentials[key] = Credential(value)

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
