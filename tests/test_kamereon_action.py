"""Test cases for vehicle actions on the Kamereon client."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_PASSWORD
from tests.const import TEST_SCHEDULES
from tests.const import TEST_USERNAME
from tests.const import TEST_VIN

from . import get_jwt
from renault_api.kamereon import Kamereon

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"
TEST_KAMEREON_VEHICLE_URL1 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
)
TEST_KAMEREON_VEHICLE_URL2 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"
)
FIXTURE_PATH = "tests/fixtures/kamereon/"
GIGYA_FIXTURE_PATH = "tests/fixtures/gigya/"

QUERY_STRING = f"country={TEST_COUNTRY}"


def get_response_content(path: str) -> str:
    """Read fixture text file as string."""
    with open(path, "r") as file:
        content = file.read()
    if path == f"{GIGYA_FIXTURE_PATH}/get_jwt.json":
        content = content.replace("sample-jwt-token", get_jwt())
    return content


@pytest.fixture
async def kamereon(websession: ClientSession) -> Kamereon:
    """Fixture for testing Kamereon."""
    kamereon = Kamereon(
        websession=websession, country=TEST_COUNTRY, locale_details=TEST_LOCALE_DETAILS
    )
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            body=get_response_content(f"{GIGYA_FIXTURE_PATH}/login.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            body=get_response_content(f"{GIGYA_FIXTURE_PATH}/account_info.json"),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.post(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            body=get_response_content(f"{GIGYA_FIXTURE_PATH}/get_jwt.json"),
            headers={"content-type": "text/javascript"},
        )
        await kamereon.login(TEST_USERNAME, TEST_PASSWORD)
        await kamereon._session.get_person_id()
        assert await kamereon._session.get_jwt_token()
    return kamereon


@pytest.mark.asyncio
async def test_vehicle_hvac_start(kamereon: Kamereon) -> None:
    """Test cars/{vin}/actions/hvac-start response."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/hvac-start?{QUERY_STRING}",
            status=200,
            body=get_response_content(
                f"{FIXTURE_PATH}/vehicle_action/hvac-start.start.json"
            ),
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
            f"{TEST_KAMEREON_VEHICLE_URL2}/actions/charge-schedule?{QUERY_STRING}",
            status=200,
            body=get_response_content(
                f"{FIXTURE_PATH}/vehicle_action/charge-schedule.schedules.json"
            ),
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
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/charge-mode?{QUERY_STRING}",
            status=200,
            body=get_response_content(
                f"{FIXTURE_PATH}/vehicle_action/charge-mode.schedule_mode.json"
            ),
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
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/charging-start?{QUERY_STRING}",
            status=200,
            body=get_response_content(
                f"{FIXTURE_PATH}/vehicle_action/charging-start.start.json"
            ),
        )
        attributes = {"action": "start"}
        assert await kamereon.set_vehicle_charging_start(
            TEST_ACCOUNT_ID,
            TEST_VIN,
            attributes,
        )
