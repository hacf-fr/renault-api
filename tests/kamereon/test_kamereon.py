"""Test cases for initialisation of the Kamereon client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests import get_jwt
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_APIKEY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN

from renault_api import kamereon

FIXTURE_PATH = "tests/fixtures/kamereon/"

TEST_JWT = get_jwt()
TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"
TEST_KAMEREON_VEHICLE_URL1 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
)
TEST_KAMEREON_VEHICLE_URL2 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"
)

QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.mark.asyncio
async def test_get_person(websession: aiohttp.ClientSession) -> None:
    """Test get_person."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/person.json"),
        )
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
async def test_get_account_vehicles(websession: aiohttp.ClientSession) -> None:
    """Test get_account_vehicles."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_ACCOUNT_URL}/vehicles?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicles/zoe_40.1.json"),
        )
        await kamereon.get_account_vehicles(
            websession=websession,
            root_url=TEST_KAMEREON_URL,
            api_key=TEST_KAMEREON_APIKEY,
            gigya_jwt=TEST_JWT,
            country=TEST_COUNTRY,
            account_id=TEST_ACCOUNT_ID,
        )


@pytest.mark.asyncio
async def test_get_vehicle_data(websession: aiohttp.ClientSession) -> None:
    """Test get_vehicle_data."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL2}/battery-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/battery-status.1.json"),
        )
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
async def test_set_vehicle_action(websession: aiohttp.ClientSession) -> None:
    """Test set_vehicle_action."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/hvac-start?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_action/hvac-start.cancel.json"
            ),
        )
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
