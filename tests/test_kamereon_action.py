"""Test cases for vehicle actions on the Kamereon client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_SCHEDULES
from tests.const import TEST_VIN
from tests.test_kamereon_init import get_logged_in_kamereon

from renault_api.kamereon import Kamereon

TEST_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_ACCOUNT_URL = f"{TEST_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"
TEST_VEHICLE_URL1 = (
    f"{TEST_ACCOUNT_URL}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/actions"
)
TEST_VEHICLE_URL2 = (
    f"{TEST_ACCOUNT_URL}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}/actions"
)

FIXTURE_PATH = "tests/fixtures/kamereon/vehicle_action"

QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
def kamereon(websession: aiohttp.ClientSession) -> Kamereon:
    """Fixture for testing Kamereon."""
    return get_logged_in_kamereon(websession=websession)


@pytest.mark.asyncio
async def test_vehicle_hvac_start(kamereon: Kamereon) -> None:
    """Test cars/{vin}/actions/hvac-start response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_VEHICLE_URL1}/hvac-start?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/hvac-start.start.json"),
        )
        attributes = {"action": "start", "targetTemperature": 21}
        assert await kamereon.set_vehicle_hvac_start(
            TEST_ACCOUNT_ID,
            TEST_VIN,
            attributes,
        )


@pytest.mark.asyncio
async def test_vehicle_charge_schedule(kamereon: Kamereon) -> None:
    """Test cars/{vin}/actions/charge-schedule response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_VEHICLE_URL2}/charge-schedule?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/charge-schedule.schedules.json"),
        )
        attributes = TEST_SCHEDULES
        assert await kamereon.set_vehicle_charge_schedule(
            TEST_ACCOUNT_ID,
            TEST_VIN,
            attributes,
        )


@pytest.mark.asyncio
async def test_vehicle_charge_mode(kamereon: Kamereon) -> None:
    """Test cars/{vin}/actions/charge-mode response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_VEHICLE_URL1}/charge-mode?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/charge-mode.schedule_mode.json"),
        )
        attributes = {"action": "schedule_mode"}
        assert await kamereon.set_vehicle_charge_mode(
            TEST_ACCOUNT_ID,
            TEST_VIN,
            attributes,
        )


@pytest.mark.asyncio
async def test_vehicle_charging_start(kamereon: Kamereon) -> None:
    """Test cars/{vin}/actions/charging-start response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_VEHICLE_URL1}/charging-start?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/charging-start.start.json"),
        )
        attributes = {"action": "start"}
        assert await kamereon.set_vehicle_charging_start(
            TEST_ACCOUNT_ID,
            TEST_VIN,
            attributes,
        )
