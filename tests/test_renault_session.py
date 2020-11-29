"""Test cases for initialisation of the Kamereon client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.test_credential_store import get_logged_in_credential_store

from renault_api.exceptions import RenaultException
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.renault_session import RenaultSession

FIXTURE_PATH = "tests/fixtures/gigya/"


def get_logged_in_session(websession: aiohttp.ClientSession) -> RenaultSession:
    """Get logged_in Kamereon."""
    return RenaultSession(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


def tests_init(websession: aiohttp.ClientSession) -> None:
    """Test initialisation."""
    assert RenaultSession(
        websession=websession,
        locale=TEST_LOCALE,
    )
    assert RenaultSession(
        websession=websession,
        country=TEST_COUNTRY,
    )
    assert RenaultSession(
        websession=websession,
        locale_details=TEST_LOCALE_DETAILS,
    )
    assert RenaultSession(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


@pytest.fixture
def session(websession: aiohttp.ClientSession) -> RenaultSession:
    """Fixture for testing Kamereon."""
    return RenaultSession(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
    )


@pytest.mark.asyncio
async def test_not_logged_in(session: RenaultSession) -> None:
    """Test valid login response."""
    with pytest.raises(
        RenaultException,
        match=f"Credential `{GIGYA_LOGIN_TOKEN}` not found in credential cache.",
    ):
        await session._get_login_token()
    with pytest.raises(
        RenaultException,
        match=f"Credential `{GIGYA_LOGIN_TOKEN}` not found in credential cache.",
    ):
        await session._get_person_id()
    with pytest.raises(
        RenaultException,
        match=f"Credential `{GIGYA_LOGIN_TOKEN}` not found in credential cache.",
    ):
        await session._get_jwt()


@pytest.mark.asyncio
async def test_login(session: RenaultSession) -> None:
    """Test valid login response."""
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
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )

        await session.login(TEST_USERNAME, TEST_PASSWORD)
        assert await session._get_login_token() == TEST_LOGIN_TOKEN
        assert len(mocked_responses.requests) == 1

        assert await session._get_person_id() == TEST_PERSON_ID
        assert len(mocked_responses.requests) == 2

        assert await session._get_jwt()
        assert len(mocked_responses.requests) == 3

        # Ensure further requests use cache
        assert await session._get_person_id() == TEST_PERSON_ID
        assert await session._get_jwt()
        assert len(mocked_responses.requests) == 3
