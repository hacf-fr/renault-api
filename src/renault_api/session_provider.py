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
from .exceptions import GigyaResponseException, KamereonException
from .gigya import Gigya
from renault_api.credential_store import CredentialStore
from renault_api.model import kamereon as model
from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential

CREDENTIAL_GIGYA_JWT = "gigya_jwt"
CREDENTIAL_GIGYA_LOGIN_TOKEN = "gigya_login_token"
CREDENTIAL_GIGYA_PERSON_ID = "gigya_person_id"

_LOGGER = logging.getLogger(__name__)


class SessionProvider:
    """Session provider."""

    def __init__(
        self,
        websession: ClientSession,
        locale_details: Dict[str, str],
        gigya: Optional[Gigya] = None,
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise session provider."""
        self._websession = websession

        self._gigya = gigya or Gigya(
            websession=websession, locale_details=locale_details
        )
        self._credentials: CredentialStore = credential_store or CredentialStore()

    async def login(self, login_id: str, password: str) -> None:
        """Forward login to Gigya, and cache the login token."""
        self._credentials.clear()
        response = await self._gigya.login(login_id, password)
        self._credentials[CREDENTIAL_GIGYA_LOGIN_TOKEN] = Credential(
            response.get_session_cookie()
        )

    async def get_person_id(self) -> str:
        """Get person id."""
        token = self._credentials.get_value(CREDENTIAL_GIGYA_PERSON_ID)
        if not token:
            login_token = self._credentials.get_value(CREDENTIAL_GIGYA_LOGIN_TOKEN)
            if not login_token:
                raise KamereonException("Login required.")
            try:
                account_response = await self._gigya.get_account_info(login_token)
            except GigyaResponseException as err:
                self.process_error(err)
                raise
            credential = Credential(account_response.get_person_id())
            self._credentials[CREDENTIAL_GIGYA_PERSON_ID] = credential
            return credential.value
        return token

    async def get_jwt_token(self) -> str:
        """Get JWT token."""
        token = self._credentials.get_value(CREDENTIAL_GIGYA_JWT)
        if not token:
            login_token = self._credentials.get_value(CREDENTIAL_GIGYA_LOGIN_TOKEN)
            if not login_token:
                raise KamereonException("Login required.")
            try:
                jwt_response = await self._gigya.get_jwt(login_token)
            except GigyaResponseException as err:
                self.process_error(err)
                raise
            credential = JWTCredential(jwt_response.get_jwt_token())
            self._credentials[CREDENTIAL_GIGYA_JWT] = credential
            return credential.value
        return token

    def process_error(self, err: GigyaResponseException):
        """Process Gigya error."""
        if err.error_code in [403005]:
            del self._credentials[CREDENTIAL_GIGYA_LOGIN_TOKEN]
