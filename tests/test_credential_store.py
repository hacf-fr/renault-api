"""Test cases for the Renault client API keys."""
from typing import Dict

from pyze.api.credentials import BasicCredentialStore  # type: ignore
from tests.const import TEST_LOCALE

from renault_api.const import AVAILABLE_LOCALES
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.const import CONF_LOCALE


def get_credential_store() -> BasicCredentialStore:
    """Build BasicCredentialStore for testing."""
    api_keys: Dict[str, str] = AVAILABLE_LOCALES[TEST_LOCALE]
    credential_store = BasicCredentialStore()
    credential_store.store(CONF_LOCALE, TEST_LOCALE, None)
    for key in [
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        credential_store.store(key, api_keys[key], None)

    return credential_store
