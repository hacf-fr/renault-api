"""Test cases for initialisation of the Kamereon client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.kamereon import Kamereon

FIXTURE_PATH = "tests/fixtures/gigya/"


@pytest.fixture
def kamereon(websession: aiohttp.ClientSession) -> Kamereon:
    """Fixture for testing Kamereon."""
    return Kamereon(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        session_provider=None,
    )


@pytest.mark.asyncio
async def test_login(kamereon: Kamereon) -> None:
    """Test valid login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)


@pytest.mark.asyncio
async def test_autoload_person_id(kamereon: Kamereon) -> None:
    """Test autoload of CREDENTIAL_GIGYA_PERSON_ID."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/account_info.json"),
            headers={"content-type": "text/javascript"},
        )
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        person_id = await kamereon._session.get_person_id()
        assert person_id == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_autoload_jwt(kamereon: Kamereon) -> None:
    """Test autoload of CREDENTIAL_GIGYA_JWT."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        assert await kamereon._session.get_jwt_token()
