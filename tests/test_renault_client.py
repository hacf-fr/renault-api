"""Test cases for the Renault client API keys."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_LOCALE_DETAILS
from tests.test_credential_store import get_logged_in_credential_store
from tests.test_renault_session import get_logged_in_session

from renault_api.renault_client import RenaultClient


@pytest.fixture
def client(websession: aiohttp.ClientSession) -> RenaultClient:
    """Fixture for testing RenaultClient."""
    return RenaultClient(
        session=get_logged_in_session(websession),
    )


def test_init(websession: aiohttp.ClientSession) -> None:
    """Test RenaultClient initialisation."""
    assert RenaultClient(
        session=get_logged_in_session(websession),
    )

    assert RenaultClient(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


@pytest.mark.asyncio
async def test_get_person(
    client: RenaultClient, mocked_responses: aioresponses
) -> None:
    """Test get_person."""
    fixtures.inject_get_person(mocked_responses)
    person = await client.get_person()
    assert len(person.accounts) == 2


@pytest.mark.asyncio
async def test_get_api_accounts(
    client: RenaultClient, mocked_responses: aioresponses
) -> None:
    """Test get_api_accounts."""
    fixtures.inject_get_person(mocked_responses)
    accounts = await client.get_api_accounts()
    assert len(accounts) == 2


@pytest.mark.asyncio
async def test_get_api_account(client: RenaultClient) -> None:
    """Test get_api_account."""
    account = await client.get_api_account(TEST_ACCOUNT_ID)
    assert account._account_id == TEST_ACCOUNT_ID
