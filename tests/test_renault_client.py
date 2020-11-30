"""Test cases for the Renault client API keys."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PERSON_ID
from tests.test_credential_store import get_logged_in_credential_store
from tests.test_renault_session import get_logged_in_session

from renault_api.renault_client import RenaultClient

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
FIXTURE_PATH = "tests/fixtures/kamereon/"
GIGYA_FIXTURE_PATH = "tests/fixtures/gigya/"
QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
def client(websession: aiohttp.ClientSession) -> RenaultClient:
    """Fixture for testing RenaultClient."""
    return RenaultClient(
        session=get_logged_in_session(websession),
    )


def tests_init(websession: aiohttp.ClientSession) -> None:
    """Test RenaultClient initialisation."""
    assert RenaultClient(
        session=get_logged_in_session(websession),
    )

    assert RenaultClient(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


@pytest.mark.asyncio
async def test_get_person(client: RenaultClient) -> None:
    """Test get_person."""
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
    """Test get_api_accounts."""
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
    """Test get_api_account."""
    account = await client.get_api_account(TEST_ACCOUNT_ID)
    assert account._account_id == TEST_ACCOUNT_ID
