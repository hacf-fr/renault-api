"""Test cases for the Renault client API keys."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests import get_file_content
from tests import get_jwt
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN

from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential
from renault_api.renault_account import RenaultAccount
from renault_api.renault_client import RenaultClient
from renault_api.session_provider import CREDENTIAL_GIGYA_JWT
from renault_api.session_provider import CREDENTIAL_GIGYA_LOGIN_TOKEN
from renault_api.session_provider import CREDENTIAL_GIGYA_PERSON_ID

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"
FIXTURE_PATH = "tests/fixtures/kamereon/"
QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
async def account(websession: ClientSession) -> RenaultAccount:
    """Fixture for testing Gigya."""
    client = RenaultClient(websession=websession, locale=TEST_LOCALE)
    client._kamereon._session._credentials[CREDENTIAL_GIGYA_LOGIN_TOKEN] = Credential(
        "sample-cookie-value"
    )
    client._kamereon._session._credentials[CREDENTIAL_GIGYA_PERSON_ID] = Credential(
        TEST_PERSON_ID
    )
    client._kamereon._session._credentials[CREDENTIAL_GIGYA_JWT] = JWTCredential(
        get_jwt()
    )
    return await client.get_api_account(TEST_ACCOUNT_ID)


@pytest.mark.asyncio
async def test_get_vehicles(account: RenaultAccount) -> None:
    """Test get_vehicles."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_ACCOUNT_URL}/vehicles?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicles/zoe_40.1.json"),
        )
        await account.get_vehicles()


@pytest.mark.asyncio
async def test_get_api_vehicles(account: RenaultAccount) -> None:
    """Test get_vehicles."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_ACCOUNT_URL}/vehicles?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicles/zoe_40.1.json"),
        )
        await account.get_api_vehicles()


@pytest.mark.asyncio
async def test_get_api_vehicle(account: RenaultAccount) -> None:
    """Test get_vehicles."""
    vehicle = await account.get_api_vehicle(TEST_VIN)
    assert vehicle._vin == TEST_VIN
