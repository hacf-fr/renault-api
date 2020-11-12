"""Test cases for the Renault client API keys."""
from typing import AsyncGenerator

import pytest
from aiohttp.client import ClientSession
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_VIN

from renault_api import renault_account
from renault_api import renault_client


@pytest.fixture
async def account() -> AsyncGenerator[renault_account.RenaultAccount, None]:
    """Fixture for testing Gigya."""
    async with ClientSession() as websession:
        client = renault_client.RenaultClient(websession=websession)
        yield await client.get_account(TEST_ACCOUNT_ID)


@pytest.mark.asyncio
async def test_get_vehicles(account: renault_account.RenaultAccount) -> None:
    """Test get_vehicles."""
    await account.get_vehicles()


@pytest.mark.asyncio
async def test_get_vehicle(account: renault_account.RenaultAccount) -> None:
    """Test get_vehicles."""
    await account.get_vehicle(TEST_VIN)
