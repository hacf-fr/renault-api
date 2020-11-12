"""Test cases for the Renault client API keys."""
import json
from typing import AsyncGenerator

import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses  # type: ignore
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_VIN
from tests.fixtures import kamereon_responses
from tests.test_renault_client import get_renault_client

from renault_api import renault_account
from renault_api.helpers import create_aiohttp_closed_event


@pytest.fixture
async def websession() -> AsyncGenerator[ClientSession, None]:
    """Fixture for generating ClientSession."""
    async with ClientSession() as aiohttp_session:
        yield aiohttp_session

        closed_event = create_aiohttp_closed_event(aiohttp_session)
        await aiohttp_session.close()
        await closed_event.wait()


async def get_renault_account(
    websession: ClientSession,
) -> renault_account.RenaultAccount:
    """Build RenaultAccount for testing."""
    client = await get_renault_client(websession)
    return client.get_account(TEST_ACCOUNT_ID)


@pytest.mark.asyncio
async def test_get_vehicles(websession: ClientSession) -> None:
    """Test account get_vehicles."""
    account = await get_renault_account(websession)
    with aioresponses() as mocked_responses:
        mocked_responses.add(
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/vehicles?country={TEST_COUNTRY}",  # noqa
            "GET",
            status=200,
            body=json.dumps(kamereon_responses.MOCK_ACCOUNTS_VEHICLES),
        )

        vehicles = await account.get_vehicles_raw()
        assert "vehicleLinks" in vehicles
        vehicle_links = vehicles["vehicleLinks"]
        assert len(vehicle_links) == 1
        assert vehicle_links[0]["vin"] == TEST_VIN
