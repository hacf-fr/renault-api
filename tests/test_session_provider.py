"""Test cases for initialisation of the Kamereon client."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from . import get_jwt
from renault_api.exceptions import GigyaResponseException
from renault_api.exceptions import SessionProviderException
from renault_api.session_provider import CREDENTIAL_GIGYA_LOGIN_TOKEN
from renault_api.session_provider import SessionProvider


def get_response_content(path: str) -> str:
    """Read fixture text file as string."""
    with open(f"tests/fixtures/{path}", "r") as file:
        content = file.read()
    if path == "gigya/get_jwt.json":
        content = content.replace("sample-jwt-token", get_jwt())
    return content


@pytest.fixture
def session_provider(websession: ClientSession) -> SessionProvider:
    """Fixture for testing Kamereon."""
    return SessionProvider(websession=websession, locale_details=TEST_LOCALE_DETAILS)


@pytest.mark.asyncio
async def test_credential_missing_login_token(
    session_provider: SessionProvider,
) -> None:
    """Test missing login_token exception."""
    expected_message = (
        f"Credential `{CREDENTIAL_GIGYA_LOGIN_TOKEN}` not found in credential cache."
    )

    with pytest.raises(SessionProviderException, match=expected_message):
        session_provider.get_login_token()

    with pytest.raises(SessionProviderException, match=expected_message):
        await session_provider.get_person_id()

    with pytest.raises(SessionProviderException, match=expected_message):
        await session_provider.get_jwt_token()


@pytest.mark.asyncio
async def test_login(session_provider: SessionProvider) -> None:
    """Test valid login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content("gigya/login.json"),
            headers={"content-type": "text/javascript"},
        )
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        login_token = session_provider.get_login_token()
        assert login_token == "sample-cookie-value"


@pytest.mark.asyncio
async def test_login_failed(session_provider: SessionProvider) -> None:
    """Test failed login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content("gigya/login.403042.json"),
            headers={"content-type": "text/javascript"},
        )
        with pytest.raises(GigyaResponseException) as excinfo:
            await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


@pytest.mark.asyncio
async def test_autoload_person_id(session_provider: SessionProvider) -> None:
    """Test autoload of CREDENTIAL_GIGYA_PERSON_ID."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content("gigya/login.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_response_content("gigya/account_info.json"),
            headers={"content-type": "text/javascript"},
        )
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        person_id = await session_provider.get_person_id()
        assert person_id == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_autoload_jwt(session_provider: SessionProvider) -> None:
    """Test autoload of CREDENTIAL_GIGYA_JWT."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content("gigya/login.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_response_content("gigya/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        assert await session_provider.get_jwt_token()
