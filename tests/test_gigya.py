"""Test cases for the Renault client API keys."""
import pytest
from aiohttp.client import ClientSession
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_USERNAME

from renault_api.gigya import Gigya


@pytest.fixture
def gigya(websession: ClientSession) -> Gigya:
    """Fixture for testing Gigya."""
    return Gigya(websession=websession, locale_details=TEST_LOCALE_DETAILS)


@pytest.mark.asyncio
async def test_login(gigya: Gigya) -> None:
    """Test valid login response."""
    login_response = await gigya.login(TEST_USERNAME, TEST_PASSWORD)
    assert login_response.get_session_cookie()


@pytest.mark.asyncio
async def test_login_failed(gigya: Gigya) -> None:
    """Test failed login response."""
    pass


@pytest.mark.asyncio
async def test_person_id(gigya: Gigya) -> None:
    """Test valid getAccountInfo response."""
    login_token = "mock"
    account_info_response = await gigya.get_account_info(login_token)
    assert account_info_response.get_person_id()


@pytest.mark.asyncio
async def test_get_jwt_token(gigya: Gigya) -> None:
    """Test valid getJWT response."""
    login_token = "mock"
    jwt_response = await gigya.get_jwt(login_token)
    assert jwt_response.id_token
