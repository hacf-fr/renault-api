"""Test cases for the Renault client API keys."""
from datetime import datetime
from datetime import timezone
from typing import List

import aiohttp
import pytest
from aioresponses import aioresponses
from aioresponses.core import RequestCall  # type:ignore
from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_VIN
from tests.test_credential_store import get_logged_in_credential_store
from tests.test_renault_session import get_logged_in_session
from yarl import URL

from renault_api.kamereon.helpers import DAYS_OF_WEEK
from renault_api.kamereon.models import ChargeSchedule
from renault_api.kamereon.models import HvacSchedule
from renault_api.renault_vehicle import RenaultVehicle


@pytest.fixture
def vehicle(websession: aiohttp.ClientSession) -> RenaultVehicle:
    """Fixture for testing RenaultVehicle."""
    return RenaultVehicle(
        account_id=TEST_ACCOUNT_ID,
        vin=TEST_VIN,
        session=get_logged_in_session(websession),
    )


def test_init(websession: aiohttp.ClientSession) -> None:
    """Test RenaultVehicle initialisation."""
    assert RenaultVehicle(
        account_id=TEST_ACCOUNT_ID,
        vin=TEST_VIN,
        session=get_logged_in_session(websession),
    )

    assert RenaultVehicle(
        account_id=TEST_ACCOUNT_ID,
        vin=TEST_VIN,
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


@pytest.mark.asyncio
async def test_get_details(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_details."""
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    assert await vehicle.get_details()

    # Ensure second call still works (ie. use cached value)
    assert await vehicle.get_details()


@pytest.mark.asyncio
async def test_get_contracts(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_contracts."""
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.1.json")
    assert await vehicle.get_contracts()

    # Ensure second call still works (ie. use cached value)
    assert await vehicle.get_contracts()


@pytest.mark.asyncio
async def test_has_contract_for_endpoint_1(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test has_contract_for_endpoint."""
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.2.json")

    assert await vehicle.has_contract_for_endpoint("battery-status")
    assert await vehicle.has_contract_for_endpoint("hvac-status")
    assert await vehicle.has_contract_for_endpoint("charge-mode")


@pytest.mark.asyncio
async def test_has_contract_for_endpoint_2(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test has_contract_for_endpoint."""
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.1.json")

    assert await vehicle.has_contract_for_endpoint("battery-status")
    assert not await vehicle.has_contract_for_endpoint("hvac-status")
    assert not await vehicle.has_contract_for_endpoint("charge-mode")


@pytest.mark.asyncio
async def test_get_battery_status(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_battery_status."""
    fixtures.inject_get_battery_status(mocked_responses)
    assert await vehicle.get_battery_status()


@pytest.mark.asyncio
async def test_get_location(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_location."""
    fixtures.inject_get_location(mocked_responses)
    assert await vehicle.get_location()


@pytest.mark.asyncio
async def test_get_hvac_status(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_hvac_status."""
    fixtures.inject_get_hvac_status(mocked_responses)
    assert await vehicle.get_hvac_status()


@pytest.mark.asyncio
async def test_get_hvac_settings(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_hvac_settings."""
    fixtures.inject_get_hvac_settings(mocked_responses)
    data = await vehicle.get_hvac_settings()

    assert data.mode == "scheduled"
    assert data.schedules
    schedules: List[HvacSchedule] = data.schedules
    assert schedules
    assert schedules[1].id == 2
    assert schedules[1].activated is True
    assert schedules[1].wednesday and schedules[1].wednesday.readyAtTime == "T15:15Z"
    assert schedules[1].friday and schedules[1].friday.readyAtTime == "T15:15Z"

    for i in (0, 2, 3, 4):
        assert schedules[i].id == i + 1
        assert schedules[i].activated is False
        for day in DAYS_OF_WEEK:
            assert schedules[i].__dict__[day] is None


@pytest.mark.asyncio
async def test_get_charge_mode(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_charge_mode."""
    fixtures.inject_get_charge_mode(mocked_responses)
    assert await vehicle.get_charge_mode()


@pytest.mark.asyncio
async def test_get_cockpit(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_cockpit."""
    fixtures.inject_get_cockpit(mocked_responses, "zoe")
    assert await vehicle.get_cockpit()


@pytest.mark.asyncio
async def test_get_lock_status(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_lock_status."""
    fixtures.inject_get_lock_status(mocked_responses)
    assert await vehicle.get_lock_status()


@pytest.mark.asyncio
async def test_get_charging_settings(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_charging_settings."""
    fixtures.inject_get_charging_settings(mocked_responses)
    assert await vehicle.get_charging_settings()


@pytest.mark.asyncio
async def test_get_notification_settings(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_notification_settings."""
    fixtures.inject_get_notification_settings(mocked_responses)
    assert await vehicle.get_notification_settings()


@pytest.mark.asyncio
async def test_get_charge_history_month(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_charge_history."""
    fixtures.inject_get_charge_history(mocked_responses, "202010", "202011", "month")
    assert await vehicle.get_charge_history(
        start=datetime(2020, 10, 1),
        end=datetime(2020, 11, 15),
        period="month",
    )


@pytest.mark.asyncio
async def test_get_charge_history_day(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_charge_history."""
    fixtures.inject_get_charge_history(mocked_responses, "20201001", "20201115", "day")
    assert await vehicle.get_charge_history(
        start=datetime(2020, 10, 1),
        end=datetime(2020, 11, 15),
        period="day",
    )


@pytest.mark.asyncio
async def test_get_charges(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_charges."""
    fixtures.inject_get_charges(mocked_responses, "20201001", "20201115")
    assert await vehicle.get_charges(
        start=datetime(2020, 10, 1),
        end=datetime(2020, 11, 15),
    )


@pytest.mark.asyncio
async def test_get_hvac_history(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_hvac_history."""
    fixtures.inject_get_hvac_history(mocked_responses, "202010", "202011", "month")
    assert await vehicle.get_hvac_history(
        start=datetime(2020, 10, 1),
        end=datetime(2020, 11, 15),
        period="month",
    )


@pytest.mark.asyncio
async def test_get_hvac_sessions(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test get_hvac_sessions."""
    fixtures.inject_get_hvac_sessions(mocked_responses, "20201001", "20201115")
    assert await vehicle.get_hvac_sessions(
        start=datetime(2020, 10, 1),
        end=datetime(2020, 11, 15),
    )


@pytest.mark.asyncio
async def test_set_ac_start(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test set_ac_start."""
    url = fixtures.inject_set_hvac_start(mocked_responses, "start")
    assert await vehicle.set_ac_start(
        21, datetime(2020, 11, 24, 6, 30, tzinfo=timezone.utc)
    )

    expected_json = {
        "data": {
            "type": "HvacStart",
            "attributes": {
                "action": "start",
                "targetTemperature": 21,
                "startDateTime": "2020-11-24T06:30:00Z",
            },
        }
    }

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]


@pytest.mark.asyncio
async def test_set_ac_stop(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test set_ac_stop."""
    url = fixtures.inject_set_hvac_start(mocked_responses, "cancel")
    assert await vehicle.set_ac_stop()

    expected_json = {"data": {"type": "HvacStart", "attributes": {"action": "cancel"}}}

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]


@pytest.mark.asyncio
async def test_set_charge_mode(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test set_charge_mode."""
    url = fixtures.inject_set_charge_mode(mocked_responses, "schedule_mode")
    assert await vehicle.set_charge_mode("schedule_mode")

    expected_json = {
        "data": {"type": "ChargeMode", "attributes": {"action": "schedule_mode"}}
    }

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]


@pytest.mark.asyncio
async def test_set_charge_schedules(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test set_charge_schedules."""
    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    schedules: List[ChargeSchedule] = []
    assert await vehicle.set_charge_schedules(schedules)

    expected_json = {
        "data": {"type": "ChargeSchedule", "attributes": {"schedules": []}}
    }

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]


@pytest.mark.asyncio
async def test_set_charge_start(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test set_charge_start."""
    url = fixtures.inject_set_charging_start(mocked_responses, "start")

    expected_json = {
        "data": {"type": "ChargingStart", "attributes": {"action": "start"}}
    }

    assert await vehicle.set_charge_start()
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]


@pytest.mark.asyncio
async def test_set_hvac_schedules(
    vehicle: RenaultVehicle, mocked_responses: aioresponses
) -> None:
    """Test set_hvac_schedules."""
    schedules: List[HvacSchedule] = []
    url = fixtures.inject_set_hvac_schedules(mocked_responses)

    assert await vehicle.set_hvac_schedules(schedules)
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]

    assert request.kwargs["json"] == {
        "data": {"type": "HvacSchedule", "attributes": {"schedules": []}}
    }
