"""Test cases for the Renault client API keys."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api import renault_client
from renault_api.exceptions import GigyaResponseException

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
FIXTURE_PATH = "tests/fixtures/kamereon/"
GIGYA_FIXTURE_PATH = "tests/fixtures/gigya/"
QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
def client(websession: ClientSession) -> renault_client.RenaultClient:
    """Fixture for testing Renault client."""
    client = renault_client.RenaultClient(
        websession=websession,
        locale=TEST_LOCALE,
    )
    return client


@pytest.mark.asyncio
async def test_login(client: renault_client.RenaultClient) -> None:
    """Test login."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        await client.login(TEST_USERNAME, TEST_PASSWORD)


@pytest.mark.asyncio
async def test_login_failed(client: renault_client.RenaultClient) -> None:
    """Test login failed."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/errors/login.403042.json"),
            headers={"content-type": "text/javascript"},
        )
        with pytest.raises(GigyaResponseException) as excinfo:
            await client.login(TEST_USERNAME, TEST_PASSWORD)
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


@pytest.mark.asyncio
async def test_get_person(client: renault_client.RenaultClient) -> None:
    """Test get_accounts."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/account_info.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.get(
            f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/person.json"),
        )
        await client.login(TEST_USERNAME, TEST_PASSWORD)
        person = await client.get_person()
        assert len(person.accounts) == 2


@pytest.mark.asyncio
async def test_get_api_accounts(client: renault_client.RenaultClient) -> None:
    """Test get_accounts."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/account_info.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_file_content(f"{GIGYA_FIXTURE_PATH}/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.get(
            f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/person.json"),
        )
        await client.login(TEST_USERNAME, TEST_PASSWORD)
        accounts = await client.get_api_accounts()
        assert len(accounts) == 2


@pytest.mark.asyncio
async def test_get_api_account(client: renault_client.RenaultClient) -> None:
    """Test get_account."""
    account = await client.get_api_account(TEST_ACCOUNT_ID)
    assert account._account_id == TEST_ACCOUNT_ID
