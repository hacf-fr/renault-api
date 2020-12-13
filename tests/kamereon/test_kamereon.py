"""Tests for Kamereon API."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_APIKEY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN

from renault_api import kamereon

TEST_JWT = fixtures.get_jwt()


@pytest.mark.asyncio
async def test_get_person(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test get_person."""
    fixtures.inject_kamereon_person(mocked_responses)

    person = await kamereon.get_person(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=TEST_JWT,
        country=TEST_COUNTRY,
        person_id=TEST_PERSON_ID,
    )
    assert len(person.accounts) == 2


@pytest.mark.asyncio
async def test_get_account_vehicles(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test get_account_vehicles."""
    fixtures.inject_kamereon_vehicles(mocked_responses)

    await kamereon.get_account_vehicles(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=TEST_JWT,
        country=TEST_COUNTRY,
        account_id=TEST_ACCOUNT_ID,
    )


@pytest.mark.asyncio
async def test_get_vehicle_data(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test get_vehicle_data."""
    fixtures.inject_kamereon_battery_status(mocked_responses)

    assert await kamereon.get_vehicle_data(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=TEST_JWT,
        country=TEST_COUNTRY,
        account_id=TEST_ACCOUNT_ID,
        vin=TEST_VIN,
        endpoint="battery-status",
    )


@pytest.mark.asyncio
async def test_set_vehicle_action(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test set_vehicle_action."""
    fixtures.inject_kamereon_action_hvac_cancel(mocked_responses)
    assert await kamereon.set_vehicle_action(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=TEST_JWT,
        country=TEST_COUNTRY,
        account_id=TEST_ACCOUNT_ID,
        vin=TEST_VIN,
        endpoint="hvac-start",
        attributes={"action": "cancel"},
    )
