"""Test cases for initialisation of the Kamereon client."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from . import get_jwt
from renault_api.exceptions import GigyaResponseException
from renault_api.exceptions import KamereonException
from renault_api.kamereon import CREDENTIAL_GIGYA_JWT
from renault_api.kamereon import CREDENTIAL_GIGYA_LOGIN_TOKEN
from renault_api.kamereon import CREDENTIAL_GIGYA_PERSON_ID
from renault_api.kamereon import Kamereon


def get_response_content(path: str) -> str:
    """Read fixture text file as string."""
    with open(f"tests/fixtures/{path}", "r") as file:
        content = file.read()
    if path == "gigya/get_jwt.json":
        content = content.replace("sample-jwt-token", get_jwt())
    return content


@pytest.fixture
def kamereon(websession: ClientSession) -> Kamereon:
    """Fixture for testing Kamereon."""
    return Kamereon(
        websession=websession, country=TEST_COUNTRY, locale_details=TEST_LOCALE_DETAILS
    )


@pytest.mark.asyncio
async def test_credential_missing_login_token(kamereon: Kamereon) -> None:
    """Test missing login_token exception."""
    expected_message = (
        f"Credential `{CREDENTIAL_GIGYA_LOGIN_TOKEN}` not found in credential cache."
    )

    with pytest.raises(KamereonException, match=expected_message):
        await kamereon._get_credential(CREDENTIAL_GIGYA_LOGIN_TOKEN)

    with pytest.raises(KamereonException, match=expected_message):
        await kamereon._get_credential(CREDENTIAL_GIGYA_PERSON_ID)

    with pytest.raises(KamereonException, match=expected_message):
        await kamereon._get_credential(CREDENTIAL_GIGYA_JWT)


@pytest.mark.asyncio
async def test_login(kamereon: Kamereon) -> None:
    """Test valid login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content("gigya/login.json"),
            headers={"content-type": "text/javascript"},
        )
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        login_token = await kamereon._get_credential(CREDENTIAL_GIGYA_LOGIN_TOKEN)
        assert login_token == "sample-cookie-value"


@pytest.mark.asyncio
async def test_login_failed(kamereon: Kamereon) -> None:
    """Test failed login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content("gigya/errors/login.403042.json"),
            headers={"content-type": "text/javascript"},
        )
        with pytest.raises(GigyaResponseException) as excinfo:
            await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


@pytest.mark.asyncio
async def test_autoload_person_id(kamereon: Kamereon) -> None:
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
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        person_id = await kamereon._get_credential(CREDENTIAL_GIGYA_PERSON_ID)
        assert person_id == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_autoload_jwt(kamereon: Kamereon) -> None:
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
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        assert await kamereon._get_credential(CREDENTIAL_GIGYA_JWT)
