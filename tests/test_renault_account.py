"""Test cases for the Renault client API keys."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_VIN
from tests.helpers import get_session_provider

from renault_api.renault_account import RenaultAccount
from renault_api.renault_client import RenaultClient

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"

FIXTURE_PATH = "tests/fixtures/kamereon/"

QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
async def account(websession: ClientSession) -> RenaultAccount:
    """Fixture for testing Gigya."""
    client = RenaultClient(websession=websession, locale=TEST_LOCALE)
    client._kamereon._session = get_session_provider()
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
