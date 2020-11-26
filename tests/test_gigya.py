"""Test cases for the Gigya client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_GIGYA_LOGIN_TOKEN
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.gigya import Gigya

FIXTURE_PATH = "tests/fixtures/gigya"


@pytest.fixture
def gigya(websession: aiohttp.ClientSession) -> Gigya:
    """Fixture for testing Gigya."""
    api_key = TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY]
    root_url = TEST_LOCALE_DETAILS[CONF_GIGYA_URL]

    return Gigya(websession=websession, api_key=api_key, root_url=root_url)


@pytest.mark.asyncio
async def test_login(gigya: Gigya) -> None:
    """Test valid login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        login_response = await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert login_response.get_session_cookie() == TEST_GIGYA_LOGIN_TOKEN


@pytest.mark.asyncio
async def test_person_id(gigya: Gigya) -> None:
    """Test valid getAccountInfo response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/account_info.json"),
            headers={"content-type": "text/javascript"},
        )
        account_info_response = await gigya.get_account_info(TEST_GIGYA_LOGIN_TOKEN)
        assert account_info_response.get_person_id() == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_get_jwt_token(gigya: Gigya) -> None:
    """Test valid getJWT response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )
        get_jwt_response = await gigya.get_jwt(TEST_GIGYA_LOGIN_TOKEN)
        assert get_jwt_response.get_jwt_token()
