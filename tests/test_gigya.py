"""Test cases for the Renault client API keys."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses  # type: ignore
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_USERNAME

from renault_api.exceptions import GigyaResponseException
from renault_api.gigya import Gigya


def get_response_content(path: str) -> str:
    """Read fixture text file as string."""
    with open(f"tests/fixtures/gigya/{path}", "r") as file:
        return file.read()


@pytest.fixture
def gigya(websession: ClientSession) -> Gigya:
    """Fixture for testing Gigya."""
    return Gigya(websession=websession, locale_details=TEST_LOCALE_DETAILS)


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
            body=get_response_content("login_failed.json"),
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
        assert account_info_response.get_person_id() == "person-id-1"


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
        assert get_jwt_response.id_token == "sample-jwt-token"
