"""Test cases for initialisation of the Kamereon client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_USERNAME
from tests.test_credential_store import get_logged_in_credential_store

from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.kamereon.client import KamereonClient

FIXTURE_PATH = "tests/fixtures/gigya/"


def get_logged_in_kamereon(websession: aiohttp.ClientSession) -> KamereonClient:
    """Get logged_in Kamereon."""
    return KamereonClient(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


@pytest.fixture
def kamereon(websession: aiohttp.ClientSession) -> KamereonClient:
    """Fixture for testing Kamereon."""
    return KamereonClient(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
    )


@pytest.mark.asyncio
async def test_login(kamereon: KamereonClient) -> None:
    """Test valid login response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        assert kamereon._credentials.get_value(GIGYA_LOGIN_TOKEN) == TEST_LOGIN_TOKEN
