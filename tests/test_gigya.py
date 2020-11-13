"""Test cases for the Renault client API keys."""
import json

import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses  # type: ignore
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.fixtures import gigya_responses

from renault_api.const import AVAILABLE_LOCALES
from renault_api.exceptions import GigyaException
from renault_api.exceptions import GigyaResponseException
from renault_api.gigya import Gigya


@pytest.fixture
def gigya(websession: ClientSession) -> Gigya:
    """Fixture for testing Gigya."""
    locale_details = AVAILABLE_LOCALES[TEST_LOCALE]
    return Gigya(websession=websession, locale_details=locale_details)


@pytest.mark.asyncio
async def test_login_ok(gigya: Gigya) -> None:
    """Test valid login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert gigya._cookie_value
        assert len(mocked_responses.requests) == 1


@pytest.mark.asyncio
async def test_login_failed(gigya: Gigya) -> None:
    """Test failed login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN_INVALID_CREDENTIAL),
            headers={"content-type": "text/javascript"},
        )

        with pytest.raises(GigyaResponseException) as excinfo:
            await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert excinfo.value.errorCode == 403042
        assert excinfo.value.errorDetails == "invalid loginID or password"


@pytest.mark.asyncio
async def test_login_missing_session(gigya: Gigya) -> None:
    """Test corrupted login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN_MISSING_SESSION),
            headers={"content-type": "text/javascript"},
        )

        with pytest.raises(GigyaException):
            await gigya.login(TEST_USERNAME, TEST_PASSWORD)


@pytest.mark.asyncio
async def test_person_id_ok(gigya: Gigya) -> None:
    """Test valid getAccountInfo response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETACCOUNTINFO),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert not gigya._person_id
        assert await gigya.get_person_id() == TEST_PERSON_ID
        assert gigya._person_id == TEST_PERSON_ID
        assert len(mocked_responses.requests) == 2

        # Ensure request count doesn't go up and cached value is used
        assert await gigya.get_person_id() == TEST_PERSON_ID
        assert len(mocked_responses.requests) == 2


@pytest.mark.asyncio
async def test_person_id_missing_data(gigya: Gigya) -> None:
    """Test corrupted getAccountInfo response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETACCOUNTINFO_MISSING_DATA),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        with pytest.raises(GigyaException):
            await gigya.get_person_id()
        assert len(mocked_responses.requests) == 2


@pytest.mark.asyncio
async def test_get_jwt_ok(gigya: Gigya) -> None:
    """Test valid getJWT response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETJWT),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert not gigya._jwt_token
        first_token = await gigya.get_jwt()
        assert first_token
        assert len(mocked_responses.requests) == 2

        # Ensure request count doesn't go up and cached value is used
        second_token = await gigya.get_jwt()
        assert second_token == first_token
        assert len(mocked_responses.requests) == 2


@pytest.mark.asyncio
async def test_get_jwt_missing_token(gigya: Gigya) -> None:
    """Test corrupted getJWT response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETJWT_MISSING_TOKEN),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        with pytest.raises(GigyaException):
            await gigya.get_jwt()
        assert len(mocked_responses.requests) == 2
