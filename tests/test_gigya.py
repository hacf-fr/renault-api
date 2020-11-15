"""Test cases for the Renault client API keys."""
import pytest
from aiohttp.client import ClientSession
from tests.const import TEST_PASSWORD
from tests.const import TEST_USERNAME

from renault_api.gigya import Gigya


@pytest.fixture
def gigya(websession: ClientSession) -> Gigya:
    """Fixture for testing Gigya."""
    return Gigya(websession=websession)


@pytest.mark.asyncio
async def test_login(gigya: Gigya) -> None:
    """Test valid login response."""
    await gigya.login(TEST_USERNAME, TEST_PASSWORD)


@pytest.mark.asyncio
async def test_login_failed(gigya: Gigya) -> None:
    """Test failed login response."""
    pass


@pytest.mark.asyncio
async def test_login_missing_session(gigya: Gigya) -> None:
    """Test corrupted login response."""
    pass


@pytest.mark.asyncio
async def test_person_id(gigya: Gigya) -> None:
    """Test valid getAccountInfo response."""
    await gigya.login(TEST_USERNAME, TEST_PASSWORD)
    await gigya.get_person_id()


@pytest.mark.asyncio
async def test_person_id_missing_data(gigya: Gigya) -> None:
    """Test corrupted getAccountInfo response."""
    pass


@pytest.mark.asyncio
async def test_get_jwt_token(gigya: Gigya) -> None:
    """Test valid getJWT response."""
    await gigya.login(TEST_USERNAME, TEST_PASSWORD)
    await gigya.get_jwt_token()


@pytest.mark.asyncio
async def test_get_jwt_token_missing_token(gigya: Gigya) -> None:
    """Test corrupted getJWT response."""
    pass
