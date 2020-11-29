"""Test cases for the Renault client API keys."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_VIN
from tests.test_credential_store import get_logged_in_credential_store
from tests.test_renault_session import get_logged_in_session

from renault_api.renault_account import RenaultAccount

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"

FIXTURE_PATH = "tests/fixtures/kamereon/"

QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
def account(websession: aiohttp.ClientSession) -> RenaultAccount:
    """Fixture for testing Gigya."""
    return RenaultAccount(
        account_id=TEST_ACCOUNT_ID,
        session=get_logged_in_session(websession),
    )


def tests_init(websession: aiohttp.ClientSession) -> None:
    """Test initialisation."""
    assert RenaultAccount(
        account_id=TEST_ACCOUNT_ID,
        session=get_logged_in_session(websession),
    )

    assert RenaultAccount(
        account_id=TEST_ACCOUNT_ID,
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


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
