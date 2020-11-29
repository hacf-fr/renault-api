"""Test cases for the Renault client API keys."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.test_renault_session import get_logged_in_session

from renault_api.renault_client import RenaultClient

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
FIXTURE_PATH = "tests/fixtures/kamereon/"
GIGYA_FIXTURE_PATH = "tests/fixtures/gigya/"
QUERY_STRING = f"country={TEST_COUNTRY}"


def get_logged_in_client(websession: aiohttp.ClientSession) -> RenaultClient:
    """Get logged_in Kamereon."""
    return RenaultClient(get_logged_in_session(websession=websession))


@pytest.fixture
def client(websession: aiohttp.ClientSession) -> RenaultClient:
    """Fixture for testing Renault client."""
    return get_logged_in_client(websession=websession)


@pytest.mark.asyncio
async def test_get_person(client: RenaultClient) -> None:
    """Test get_accounts."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/person.json"),
        )
        person = await client.get_person()
        assert len(person.accounts) == 2


@pytest.mark.asyncio
async def test_get_api_accounts(client: RenaultClient) -> None:
    """Test get_accounts."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/person.json"),
        )
        accounts = await client.get_api_accounts()
        assert len(accounts) == 2


@pytest.mark.asyncio
async def test_get_api_account(client: RenaultClient) -> None:
    """Test get_account."""
    account = await client.get_api_account(TEST_ACCOUNT_ID)
    assert account._account_id == TEST_ACCOUNT_ID
