"""Test cases for the Renault client API keys."""
import json

import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses  # type: ignore
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.fixtures import gigya_responses
from tests.fixtures import kamereon_responses

from renault_api import renault_client
from renault_api.exceptions import RenaultException


async def get_renault_client(websession: ClientSession) -> renault_client.RenaultClient:
    """Build RenaultClient for testing."""
    client = renault_client.RenaultClient(websession=websession, locale=TEST_LOCALE)

    with aioresponses() as mocked_responses:
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.login",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETACCOUNTINFO),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETJWT),
            headers={"content-type": "text/javascript"},
        )
        await client.login(TEST_USERNAME, TEST_PASSWORD)
        await client._gigya.get_person_id()
        await client._gigya.get_jwt()

    return client


@pytest.mark.asyncio
async def test_invalid_locale(websession: ClientSession) -> None:
    """Test client get_accounts."""
    with pytest.raises(RenaultException):
        renault_client.RenaultClient(websession=websession, locale="azerty")


@pytest.mark.asyncio
async def test_get_accounts(websession: ClientSession) -> None:
    """Test client get_accounts."""
    client = await get_renault_client(websession=websession)
    with aioresponses() as mocked_responses:
        mocked_responses.add(
            f"{TEST_KAMEREON_URL}/commerce/v1/persons/{TEST_PERSON_ID}?country={TEST_COUNTRY}",  # noqa
            "GET",
            status=200,
            body=json.dumps(kamereon_responses.MOCK_PERSONS),
        )
        get_accounts = await client.get_accounts()
        assert len(mocked_responses.requests) == 1

        assert len(get_accounts) == 2

        account_id = get_accounts[0].account_id
        assert account_id == TEST_ACCOUNT_ID
