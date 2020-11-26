"""Test cases for the Renault client API keys."""
from datetime import datetime
from tests.helpers import get_session_provider
from typing import List

import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests import get_file_content
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_VIN

from renault_api.model.kamereon import ChargeMode
from renault_api.model.kamereon import ChargeSchedule
from renault_api.renault_client import RenaultClient
from renault_api.renault_vehicle import RenaultVehicle


TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"
TEST_KAMEREON_VEHICLE_URL1 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
)
TEST_KAMEREON_VEHICLE_URL2 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"
)
FIXTURE_PATH = "tests/fixtures/kamereon/"
QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
async def vehicle(websession: ClientSession) -> RenaultVehicle:
    """Fixture for testing Gigya."""
    client = RenaultClient(websession=websession, locale=TEST_LOCALE)
    client._kamereon._session = get_session_provider()
    account = await client.get_api_account(TEST_ACCOUNT_ID)
    return await account.get_api_vehicle(TEST_VIN)


@pytest.mark.asyncio
async def test_get_battery_status(vehicle: RenaultVehicle) -> None:
    """Test get_battery_status."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL2}/battery-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/battery-status.1.json"),
        )
        assert await vehicle.get_battery_status()


@pytest.mark.asyncio
async def test_get_location(vehicle: RenaultVehicle) -> None:
    """Test get_location."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/location?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/location.json"),
        )
        assert await vehicle.get_location()


@pytest.mark.asyncio
async def test_get_hvac_status(vehicle: RenaultVehicle) -> None:
    """Test get_hvac_status."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/hvac-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/hvac-status.json"),
        )
        assert await vehicle.get_hvac_status()


@pytest.mark.asyncio
async def test_get_charge_mode(vehicle: RenaultVehicle) -> None:
    """Test get_charge_mode."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/charge-mode?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/charge-mode.json"),
        )
        assert await vehicle.get_charge_mode()


@pytest.mark.asyncio
async def test_get_cockpit(vehicle: RenaultVehicle) -> None:
    """Test get_cockpit."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL2}/cockpit?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/cockpit.zoe.json"),
        )
        assert await vehicle.get_cockpit()


@pytest.mark.asyncio
async def test_get_lock_status(vehicle: RenaultVehicle) -> None:
    """Test get_lock_status."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/lock-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/lock-status.json"),
        )
        assert await vehicle.get_lock_status()


@pytest.mark.asyncio
async def test_get_charging_settings(vehicle: RenaultVehicle) -> None:
    """Test get_charging_settings."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/charging-settings?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_data/charging-settings.json"
            ),
        )
        assert await vehicle.get_charging_settings()


@pytest.mark.asyncio
async def test_get_notification_settings(vehicle: RenaultVehicle) -> None:
    """Test get_notification_settings."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/notification-settings?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_data/notification-settings.json"
            ),
        )
        assert await vehicle.get_notification_settings()


@pytest.mark.asyncio
async def test_get_charge_history(vehicle: RenaultVehicle) -> None:
    """Test get_charge_history."""
    query_string = f"{QUERY_STRING}&end=202011&start=202010&type=month"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/charge-history?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/charge-history.json"),
        )
        assert await vehicle.get_charge_history(
            start=datetime(2020, 10, 1),
            end=datetime(2020, 11, 15),
        )


@pytest.mark.asyncio
async def test_get_charges(vehicle: RenaultVehicle) -> None:
    """Test get_charges."""
    query_string = f"{QUERY_STRING}&end=20201115&start=20201001"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/charges?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/charges.json"),
        )
        assert await vehicle.get_charges(
            start=datetime(2020, 10, 1),
            end=datetime(2020, 11, 15),
        )


@pytest.mark.asyncio
async def test_get_hvac_history(vehicle: RenaultVehicle) -> None:
    """Test get_hvac_history."""
    query_string = f"{QUERY_STRING}&end=202011&start=202010&type=month"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/hvac-history?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/hvac-history.json"),
        )
        assert await vehicle.get_hvac_history(
            start=datetime(2020, 10, 1),
            end=datetime(2020, 11, 15),
        )


@pytest.mark.asyncio
async def test_get_hvac_sessions(vehicle: RenaultVehicle) -> None:
    """Test get_hvac_sessions."""
    query_string = f"{QUERY_STRING}&end=20201115&start=20201001"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/hvac-sessions?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/hvac-sessions.json"),
        )
        assert await vehicle.get_hvac_sessions(
            start=datetime(2020, 10, 1),
            end=datetime(2020, 11, 15),
        )


@pytest.mark.asyncio
async def test_set_ac_start(vehicle: RenaultVehicle) -> None:
    """Test set_ac_start."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/hvac-start?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_action/hvac-start.start.json"
            ),
        )
        assert await vehicle.set_ac_start(21, datetime(2020, 11, 24))


@pytest.mark.asyncio
async def test_set_ac_stop(vehicle: RenaultVehicle) -> None:
    """Test set_ac_stop."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/hvac-start?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_action/hvac-start.cancel.json"
            ),
        )
        assert await vehicle.set_ac_stop()


@pytest.mark.asyncio
async def test_set_charge_mode(vehicle: RenaultVehicle) -> None:
    """Test set_charge_mode."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/charge-mode?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_action/charge-mode.schedule_mode.json"
            ),
        )
        assert await vehicle.set_charge_mode(ChargeMode.SCHEDULE_MODE)


@pytest.mark.asyncio
async def test_set_charge_schedules(vehicle: RenaultVehicle) -> None:
    """Test set_charge_schedules."""
    schedules: List[ChargeSchedule] = []
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_KAMEREON_VEHICLE_URL2}/actions/charge-schedule?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_action/charge-schedule.schedules.json"
            ),
        )
        assert await vehicle.set_charge_schedules(schedules)


@pytest.mark.asyncio
async def test_set_charge_start(vehicle: RenaultVehicle) -> None:
    """Test set_charge_start."""
    with aioresponses() as mocked_responses:
        mocked_responses.post(
            f"{TEST_KAMEREON_VEHICLE_URL1}/actions/charging-start?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_action/charging-start.start.json"
            ),
        )
        assert await vehicle.set_charge_start()
