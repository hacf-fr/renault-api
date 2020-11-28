"""Session provider for interaction with Renault servers."""
import logging
from typing import Dict
from typing import Optional

import aiohttp

from renault_api import gigya
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import CredentialStore
from renault_api.gigya.exceptions import GigyaException


_LOGGER = logging.getLogger(__name__)


class RenaultSession:
    """Kamereon client for interaction with Renault servers."""

    def __init__(
        self,
        websession: aiohttp.ClientSession,
        country: str,
        locale_details: Dict[str, str],
        credential_store: Optional[CredentialStore] = None,
    ) -> None:
        """Initialise SessionProvider."""
        self._websession = websession

        self._country = country
        self._kamereon_api_key = locale_details[CONF_KAMEREON_APIKEY]
        self._kamereon_root_url = locale_details[CONF_KAMEREON_URL]
        self._gigya_api_key = locale_details[CONF_GIGYA_APIKEY]
        self._gigya_root_url = locale_details[CONF_GIGYA_URL]
        self._credentials: CredentialStore = credential_store or CredentialStore()

    @property
    def websession(self) -> aiohttp.ClientSession:
        """Get websession."""
        return self._websession

    @property
    def kamereon_api_key(self) -> str:
        """Get kamereon api key."""
        return self._kamereon_api_key

    @property
    def kamereon_root_url(self) -> str:
        """Get kamereon root url."""
        return self._kamereon_root_url

    @property
    def country(self) -> str:
        """Get country."""
        return self._country

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

    def _get_login_token(self) -> str:
        login_token = self._credentials.get_value(gigya.GIGYA_LOGIN_TOKEN)
        if login_token:
            return login_token
        raise GigyaException(
            f"Credential `{gigya.GIGYA_LOGIN_TOKEN}` not found in credential cache."
        )

    async def get_person_id(self) -> str:
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

    async def get_jwt(self) -> str:
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
