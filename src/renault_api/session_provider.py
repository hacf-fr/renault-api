"""Kamereon client for interaction with Renault servers."""
import logging
from typing import Optional

import aiohttp

from .credential_store import CredentialStore
from .exceptions import GigyaResponseException
from .exceptions import SessionProviderException
from .gigya import Gigya
from .model.credential import Credential
from .model.credential import JWTCredential

_LOGGER = logging.getLogger(__name__)

GIGYA_JWT = "gigya_jwt"
GIGYA_REFRESH_TOKEN = "gigya_refresh_token"
GIGYA_PERSON_ID = "gigya_person_id"


class BaseSessionProvider:  # pragma: no cover
    """Base session provider."""

    async def login(self, login_id: str, password: str) -> None:
        """Forward login to Gigya, and cache the login token."""
        raise NotImplementedError

    async def get_person_id(self) -> str:
        """Get person id."""
        raise NotImplementedError

    async def get_jwt_token(self) -> str:
        """Get JWT token."""
        raise NotImplementedError


class GigyaSessionProvider(BaseSessionProvider):
    """Gigya session provider."""

    def __init__(
        self,
        websession: aiohttp.ClientSession,
        api_key: Optional[str] = None,
        root_url: Optional[str] = None,
        gigya: Optional[Gigya] = None,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise session provider."""
        self._websession = websession
        self._credentials: CredentialStore = credential_store or CredentialStore()
        if not gigya:
            if not api_key:
                raise ValueError("`api_key` must be provided if gigya is None")
            if not root_url:
                raise ValueError("`root_url` must be provided if gigya is None")
            gigya = Gigya(websession=websession, api_key=api_key, root_url=root_url)
        self._gigya = gigya

    async def login(self, login_id: str, password: str) -> None:
        """Forward login to Gigya, and cache the login token."""
        self._credentials.clear()
        response = await self._gigya.login(login_id, password)
        self._credentials[GIGYA_REFRESH_TOKEN] = Credential(
            response.get_session_cookie()
        )

    def get_login_token(self) -> str:
        """Get login token."""
        login_token = self._credentials.get_value(GIGYA_REFRESH_TOKEN)
        if not login_token:
            raise SessionProviderException(
                f"Credential `{GIGYA_REFRESH_TOKEN}` " "not found in credential cache."
            )
        return login_token

    async def get_person_id(self) -> str:
        """Get person id."""
        person_id = self._credentials.get_value(GIGYA_PERSON_ID)
        if not person_id:
            login_token = self.get_login_token()
            try:
                account_response = await self._gigya.get_account_info(login_token)
            except GigyaResponseException as err:
                self.process_error(err)
                raise
            person_id = account_response.get_person_id()
            self._credentials[GIGYA_PERSON_ID] = Credential(person_id)
        return person_id

    async def get_jwt_token(self) -> str:
        """Get JWT token."""
        jwt_token = self._credentials.get_value(GIGYA_JWT)
        if not jwt_token:
            login_token = self.get_login_token()
            try:
                jwt_response = await self._gigya.get_jwt(login_token)
            except GigyaResponseException as err:
                self.process_error(err)
                raise
            jwt_token = jwt_response.get_jwt_token()
            self._credentials[GIGYA_JWT] = JWTCredential(jwt_token)
        return jwt_token

    def process_error(self, err: GigyaResponseException) -> None:
        """Process Gigya error."""
        # if err.error_code in [403005, 433013]:
        _LOGGER.warning(
            "Refresh token cleared due to Gigya error %s (%s).",
            err.error_code,
            err.error_details,
        )
        del self._credentials[GIGYA_REFRESH_TOKEN]
