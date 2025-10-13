"""Test suite for the renault_api CLI."""

import os

from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_LOCALE
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN
from tests.fixtures import get_jwt

from renault_api.cli.renault_settings import CONF_ACCOUNT_ID
from renault_api.cli.renault_settings import CONF_VIN
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import FileCredentialStore
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya import GIGYA_PERSON_ID


def initialise_credential_store(
    include_account_id: bool | None = None,
    include_vin: bool | None = None,
) -> None:
    """Initialise CLI credential store."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(get_jwt())
    if include_account_id:
        credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    if include_vin:
        credential_store[CONF_VIN] = Credential(TEST_VIN)
