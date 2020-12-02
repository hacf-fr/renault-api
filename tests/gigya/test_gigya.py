"""Tests for Gigya API."""
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

from renault_api import gigya
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL

FIXTURE_PATH = "tests/fixtures/gigya"


TEST_API_KEY = TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY]
TEST_ROOT_URL = TEST_LOCALE_DETAILS[CONF_GIGYA_URL]


@pytest.mark.asyncio
async def test_login(websession: aiohttp.ClientSession) -> None:
    """Test login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        response = await gigya.login(
            websession,
            TEST_ROOT_URL,
            TEST_API_KEY,
            TEST_USERNAME,
            TEST_PASSWORD,
        )
        assert response.get_session_cookie() == TEST_LOGIN_TOKEN


@pytest.mark.asyncio
async def test_person_id(websession: aiohttp.ClientSession) -> None:
    """Test get_account_info response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/get_account_info.json"),
            headers={"content-type": "text/javascript"},
        )

        response = await gigya.get_account_info(
            websession, TEST_ROOT_URL, TEST_API_KEY, TEST_LOGIN_TOKEN
        )
        assert response.get_person_id() == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_get_jwt_token(websession: aiohttp.ClientSession) -> None:
    """Test get_jwt response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )

        response = await gigya.get_jwt(
            websession,
            TEST_ROOT_URL,
            TEST_API_KEY,
            TEST_LOGIN_TOKEN,
        )
        assert response.get_jwt()
