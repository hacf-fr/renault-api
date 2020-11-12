"""Test cases for the Renault client API keys."""
from typing import AsyncGenerator

import pytest
from aiohttp.client import ClientSession
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_PASSWORD
from tests.const import TEST_USERNAME

from renault_api import renault_client


@pytest.fixture
async def client() -> AsyncGenerator[renault_client.RenaultClient, None]:
    """Fixture for testing Gigya."""
    async with ClientSession() as websession:
        yield renault_client.RenaultClient(websession=websession)


@pytest.mark.asyncio
async def test_login(client: renault_client.RenaultClient) -> None:
    """Test login."""
    await client.login(TEST_USERNAME, TEST_PASSWORD)


@pytest.mark.asyncio
async def test_get_accounts(client: renault_client.RenaultClient) -> None:
    """Test get_accounts."""
    await client.get_accounts()


@pytest.mark.asyncio
async def test_get_account(client: renault_client.RenaultClient) -> None:
    """Test get_account."""
    await client.get_account(TEST_ACCOUNT_ID)
