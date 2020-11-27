"""Test cases for the Gigya client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.test_credential_store import get_logged_in_credential_store

from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.exceptions import GigyaException
from renault_api.gigya import Gigya
from renault_api.gigya import GIGYA_LOGIN_TOKEN

FIXTURE_PATH = "tests/fixtures/gigya"


def get_logged_in_gigya(websession: aiohttp.ClientSession) -> Gigya:
    """Get valid Gigya for mocking Kamereon."""
    return Gigya(
        websession=websession,
        api_key=TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY],
        root_url=TEST_LOCALE_DETAILS[CONF_GIGYA_URL],
        credential_store=get_logged_in_credential_store(),
    )


@pytest.fixture
def gigya(websession: aiohttp.ClientSession) -> Gigya:
    """Fixture for testing Gigya."""
    return Gigya(
        websession=websession,
        api_key=TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY],
        root_url=TEST_LOCALE_DETAILS[CONF_GIGYA_URL],
    )


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
        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert gigya._credentials.get_value(GIGYA_LOGIN_TOKEN) == TEST_LOGIN_TOKEN


@pytest.mark.asyncio
async def test_person_id(gigya: Gigya) -> None:
    """Test valid getAccountInfo response."""
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

        with pytest.raises(
            GigyaException,
            match=f"Credential `{GIGYA_LOGIN_TOKEN}` not found in credential cache.",
        ):
            await gigya.get_person_id()

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert await gigya.get_person_id() == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_get_jwt_token(gigya: Gigya) -> None:
    """Test valid getJWT response."""
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

        with pytest.raises(
            GigyaException,
            match=f"Credential `{GIGYA_LOGIN_TOKEN}` not found in credential cache.",
        ):
            await gigya.get_jwt()

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert await gigya.get_jwt()
