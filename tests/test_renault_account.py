"""Test cases for the Renault client API keys."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_VIN
from tests.test_renault_client import get_logged_in_client

from renault_api.renault_account import RenaultAccount

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"

FIXTURE_PATH = "tests/fixtures/kamereon/"

QUERY_STRING = f"country={TEST_COUNTRY}"


async def get_logged_in_account(websession: aiohttp.ClientSession) -> RenaultAccount:
    """Get logged_in Kamereon."""
    client = get_logged_in_client(websession)
    return await client.get_api_account(TEST_ACCOUNT_ID)


@pytest.fixture
async def account(websession: aiohttp.ClientSession) -> RenaultAccount:
    """Fixture for testing Gigya."""
    return await get_logged_in_account(websession)


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
