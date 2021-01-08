"""Test cases for the Renault client API keys."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_VIN
from tests.test_credential_store import get_logged_in_credential_store
from tests.test_renault_session import get_logged_in_session

from renault_api.renault_account import RenaultAccount


@pytest.fixture
def account(websession: aiohttp.ClientSession) -> RenaultAccount:
    """Fixture for testing RenaultAccount."""
    return RenaultAccount(
        account_id=TEST_ACCOUNT_ID,
        session=get_logged_in_session(websession),
    )


def tests_init(websession: aiohttp.ClientSession) -> None:
    """Test RenaultAccount initialisation."""
    assert RenaultAccount(
        account_id=TEST_ACCOUNT_ID,
        session=get_logged_in_session(websession),
    )

    assert RenaultAccount(
        account_id=TEST_ACCOUNT_ID,
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


@pytest.mark.asyncio
async def test_get_vehicles(
    account: RenaultAccount, mocked_responses: aioresponses
) -> None:
    """Test get_vehicles."""
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")
    await account.get_vehicles()


@pytest.mark.asyncio
async def test_get_api_vehicles(
    account: RenaultAccount, mocked_responses: aioresponses
) -> None:
    """Test get_api_vehicles."""
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")
    await account.get_api_vehicles()


@pytest.mark.asyncio
async def test_get_api_vehicle(account: RenaultAccount) -> None:
    """Test get_api_vehicle."""
    vehicle = await account.get_api_vehicle(TEST_VIN)
    assert vehicle._vin == TEST_VIN
