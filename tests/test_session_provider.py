"""Test cases for initialisation of the Kamereon client."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.exceptions import GigyaResponseException
from renault_api.exceptions import SessionProviderException
from renault_api.gigya import Gigya
from renault_api.session_provider import GIGYA_REFRESH_TOKEN
from renault_api.session_provider import GigyaSessionProvider

FIXTURE_PATH = "tests/fixtures/gigya"


@pytest.fixture
def session_provider(websession: ClientSession) -> GigyaSessionProvider:
    """Fixture for testing Kamereon."""
    api_key = TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY]
    root_url = TEST_LOCALE_DETAILS[CONF_GIGYA_URL]
    return GigyaSessionProvider(
        websession=websession, api_key=api_key, root_url=root_url
    )


def test_init(websession: ClientSession) -> None:
    """Fixture for testing Kamereon."""
    api_key = TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY]
    root_url = TEST_LOCALE_DETAILS[CONF_GIGYA_URL]

    with pytest.raises(ValueError):
        assert GigyaSessionProvider(websession=websession)

    with pytest.raises(ValueError):
        assert GigyaSessionProvider(websession=websession, api_key=api_key)

    assert GigyaSessionProvider(
        websession=websession, api_key=api_key, root_url=root_url
    )

    assert GigyaSessionProvider(
        websession=websession,
        gigya=Gigya(websession=websession, api_key=api_key, root_url=root_url),
    )


@pytest.mark.asyncio
async def test_credential_missing_login_token(
    session_provider: GigyaSessionProvider,
) -> None:
    """Test missing login_token exception."""
    expected_message = (
        f"Credential `{GIGYA_REFRESH_TOKEN}` not found in credential cache."
    )

    with pytest.raises(SessionProviderException, match=expected_message):
        await session_provider.get_person_id()

    with pytest.raises(SessionProviderException, match=expected_message):
        await session_provider.get_jwt_token()


@pytest.mark.asyncio
async def test_login(session_provider: GigyaSessionProvider) -> None:
    """Test valid login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)


@pytest.mark.asyncio
async def test_login_failed(session_provider: GigyaSessionProvider) -> None:
    """Test failed login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/errors/403042.json"),
            headers={"content-type": "text/javascript"},
        )
        with pytest.raises(GigyaResponseException) as excinfo:
            await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


@pytest.mark.asyncio
async def test_autoload_person_id(session_provider: GigyaSessionProvider) -> None:
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
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        assert len(mocked_responses.requests) == 1
        assert await session_provider.get_person_id() == TEST_PERSON_ID
        assert len(mocked_responses.requests) == 2
        assert await session_provider.get_person_id() == TEST_PERSON_ID
        assert len(mocked_responses.requests) == 2


@pytest.mark.asyncio
async def test_error_person_id(session_provider: GigyaSessionProvider) -> None:
    """Test autoload of CREDENTIAL_GIGYA_JWT."""
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
            body=get_file_content(f"{FIXTURE_PATH}/errors/403005.json"),
            headers={"content-type": "text/javascript"},
        )
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        assert GIGYA_REFRESH_TOKEN in session_provider._credentials

        with pytest.raises(GigyaResponseException):
            assert await session_provider.get_person_id()
        assert GIGYA_REFRESH_TOKEN not in session_provider._credentials


@pytest.mark.asyncio
async def test_autoload_jwt(session_provider: GigyaSessionProvider) -> None:
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
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        assert len(mocked_responses.requests) == 1
        assert await session_provider.get_jwt_token()
        assert len(mocked_responses.requests) == 2
        assert await session_provider.get_jwt_token()
        assert len(mocked_responses.requests) == 2


@pytest.mark.asyncio
async def test_error_jwt(session_provider: GigyaSessionProvider) -> None:
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
            body=get_file_content(f"{FIXTURE_PATH}/errors/403005.json"),
            headers={"content-type": "text/javascript"},
        )
        await session_provider.login(TEST_USERNAME, TEST_PASSWORD)
        assert GIGYA_REFRESH_TOKEN in session_provider._credentials

        with pytest.raises(GigyaResponseException):
            assert await session_provider.get_jwt_token()
        assert GIGYA_REFRESH_TOKEN not in session_provider._credentials
