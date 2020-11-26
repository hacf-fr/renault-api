"""Kamereon client for interaction with Renault servers."""
import logging
from typing import Optional

from aiohttp import ClientSession

from .exceptions import GigyaResponseException
from .exceptions import SessionProviderException
from .gigya import Gigya
from renault_api.credential_store import CredentialStore
from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential

CREDENTIAL_GIGYA_JWT = "gigya_jwt"
CREDENTIAL_GIGYA_LOGIN_TOKEN = "gigya_login_token"
CREDENTIAL_GIGYA_PERSON_ID = "gigya_person_id"

_LOGGER = logging.getLogger(__name__)


class BaseSessionProvider:  # pragma: no cover
    """Base session provider."""

    def __init__(
        self,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise session provider."""
        self._credentials: CredentialStore = credential_store or CredentialStore()

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
        websession: ClientSession,
        api_key: Optional[str],
        root_url: Optional[str],
        gigya: Optional[Gigya] = None,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise session provider."""
        super().__init__(credential_store)
        self._websession = websession
        if not gigya:
            if not api_key:
                raise ValueError
            if not root_url:
                raise ValueError
            gigya = Gigya(websession=websession, api_key=api_key, root_url=root_url)
        self._gigya = gigya

    async def login(self, login_id: str, password: str) -> None:
        """Forward login to Gigya, and cache the login token."""
        self._credentials.clear()
        response = await self._gigya.login(login_id, password)
        self._credentials[CREDENTIAL_GIGYA_LOGIN_TOKEN] = Credential(
            response.get_session_cookie()
        )

    def get_login_token(self) -> str:
        """Get login token."""
        login_token = self._credentials.get_value(CREDENTIAL_GIGYA_LOGIN_TOKEN)
        if not login_token:
            raise SessionProviderException(
                f"Credential `{CREDENTIAL_GIGYA_LOGIN_TOKEN}` "
                "not found in credential cache."
            )
        return login_token

    async def get_person_id(self) -> str:
        """Get person id."""
        person_id = self._credentials.get_value(CREDENTIAL_GIGYA_PERSON_ID)
        if not person_id:
            login_token = self.get_login_token()
            try:
                account_response = await self._gigya.get_account_info(login_token)
            except GigyaResponseException as err:
                self.process_error(err)
                raise
            person_id = account_response.get_person_id()
            self._credentials[CREDENTIAL_GIGYA_PERSON_ID] = Credential(person_id)
        return person_id

    async def get_jwt_token(self) -> str:
        """Get JWT token."""
        jwt_token = self._credentials.get_value(CREDENTIAL_GIGYA_JWT)
        if not jwt_token:
            login_token = self.get_login_token()
            try:
                jwt_response = await self._gigya.get_jwt(login_token)
            except GigyaResponseException as err:
                self.process_error(err)
                raise
            jwt_token = jwt_response.get_jwt_token()
            self._credentials[CREDENTIAL_GIGYA_JWT] = JWTCredential(jwt_token)
        return jwt_token

    def process_error(self, err: GigyaResponseException) -> None:
        """Process Gigya error."""
        if err.error_code in [403005]:
            del self._credentials[CREDENTIAL_GIGYA_LOGIN_TOKEN]
