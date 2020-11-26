"""Test cases for the Gigya client."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests import get_jwt
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.exceptions import GigyaResponseException
from renault_api.gigya import Gigya


def get_response_content(path: str) -> str:
    """Read fixture text file as string."""
    with open(f"tests/fixtures/gigya/{path}", "r") as file:
        content = file.read()
    if path == "get_jwt.json":
        content = content.replace("sample-jwt-token", get_jwt())
    return content


@pytest.fixture
def gigya(websession: ClientSession) -> Gigya:
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
            body=get_response_content("login.json"),
            headers={"content-type": "text/javascript"},
        )
        login_response = await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert login_response.get_session_cookie() == "sample-cookie-value"


@pytest.mark.asyncio
async def test_login_failed(gigya: Gigya) -> None:
    """Test failed login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content("errors/login.403042.json"),
            headers={"content-type": "text/javascript"},
        )
        with pytest.raises(GigyaResponseException) as excinfo:
            await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


@pytest.mark.asyncio
async def test_person_id(gigya: Gigya) -> None:
    """Test valid getAccountInfo response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_response_content("account_info.json"),
            headers={"content-type": "text/javascript"},
        )
        account_info_response = await gigya.get_account_info("sample-cookie-value")
        assert account_info_response.get_person_id() == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_get_jwt_token(gigya: Gigya) -> None:
    """Test valid getJWT response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_response_content("get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )
        get_jwt_response = await gigya.get_jwt("sample-cookie-value")
        assert get_jwt_response.get_jwt_token()
