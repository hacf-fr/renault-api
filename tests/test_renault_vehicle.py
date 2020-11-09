"""Test cases for the Renault client API keys."""
from datetime import datetime

import pytest
import requests
import responses  # type: ignore
from pyze.api.kamereon import PERIOD_FORMATS  # type: ignore
from pyze.api.schedule import ChargeMode  # type: ignore
from pyze.api.schedule import ChargeSchedules
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_VIN
from tests.fixtures import kamereon_responses
from tests.test_renault_account import get_renault_account

from renault_api.renault_vehicle import RenaultVehicle


def get_renault_vehicle() -> RenaultVehicle:
    """Build RenaultVehicle for testing."""
    return get_renault_account().get_vehicle(TEST_VIN)


@responses.activate  # type: ignore
def test_battery_status() -> None:
    """Test vehicle battery_status."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}/battery-status?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLE_BATTERY_STATUS,
        )

        battery_status = renault_vehicle.battery_status()
        for key in [
            "timestamp",
            "batteryLevel",
            "batteryTemperature",
            "batteryAutonomy",
            "batteryCapacity",
            "batteryAvailableEnergy",
            "plugStatus",
            "chargingStatus",
        ]:
            assert key in battery_status


@responses.activate  # type: ignore
def test_mileage() -> None:
    """Test vehicle mileage."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}/cockpit?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLE_COCKPIT,
        )

        mileage = renault_vehicle.mileage()
        for key in [
            "totalMileage",
        ]:
            assert key in mileage


@responses.activate  # type: ignore
def test_hvac_status() -> None:
    """Test vehicle hvac_status."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/hvac-status?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLE_HVAC_STATUS,
        )

        hvac_status = renault_vehicle.hvac_status()
        for key in [
            "hvacStatus",
            "externalTemperature",
        ]:
            assert key in hvac_status


def test_location_not_supported() -> None:
    """Test vehicle location."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/location?country={TEST_COUNTRY}",  # noqa
            status=501,
            json=kamereon_responses.MOCK_VEHICLE_LOCATION_NOT_SUPPORTED,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.location()


def test_charge_mode_invalid_upstream() -> None:
    """Test vehicle charge-mode."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/charge-mode?country={TEST_COUNTRY}",  # noqa
            status=500,
            json=kamereon_responses.MOCK_VEHICLE_CHARGE_MODE_INVALID_UPSTREAM,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.charge_mode()


def test_lock_status_not_supported() -> None:
    """Test vehicle lock-status."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/lock-status?country={TEST_COUNTRY}",  # noqa
            status=501,
            json=kamereon_responses.MOCK_VEHICLE_LOCK_STATUS_NOT_SUPPORTED,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.lock_status()


def test_charge_schedules_invalid_upstream() -> None:
    """Test vehicle charging-settings."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/charging-settings?country={TEST_COUNTRY}",  # noqa
            status=500,
            json=kamereon_responses.MOCK_VEHICLE_CHARGING_SETTINGS_INVALID_UPSTREAM,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.charge_schedules()


def test_notification_settings_invalid_upstream() -> None:
    """Test vehicle notification-settings."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/notification-settings?country={TEST_COUNTRY}",  # noqa
            status=500,
            json=kamereon_responses.MOCK_VEHICLE_NOTIFICATION_SETTINGS_INVALID_UPSTREAM,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.notification_settings()


def test_charge_history_empty() -> None:
    """Test vehicle charges."""
    renault_vehicle = get_renault_vehicle()
    start = datetime(2020, 9, 1)
    end = datetime(2020, 10, 1)
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/charges?start={start.strftime('%Y%m%d')}&end={end.strftime('%Y%m%d')}&country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLE_CHARGES_EMPTY,
        )

        charge_history = renault_vehicle.charge_history(start, end)
    assert charge_history == []


def test_charge_statistics_empty() -> None:
    """Test vehicle charge-history."""
    renault_vehicle = get_renault_vehicle()
    start = datetime(2020, 9, 1)
    end = datetime(2020, 10, 1)
    period = "month"
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/charge-history?type={period}&start={start.strftime(PERIOD_FORMATS[period])}&end={end.strftime(PERIOD_FORMATS[period])}&country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLE_CHARGE_HISTORY_EMPTY,
        )

        charge_statistics = renault_vehicle.charge_statistics(start, end, period)
    assert charge_statistics == []


def test_hvac_history_invalid_upstream() -> None:
    """Test vehicle hvac-sessions."""
    renault_vehicle = get_renault_vehicle()
    start = datetime(2020, 9, 1)
    end = datetime(2020, 10, 1)
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/hvac-sessions?start={start.strftime('%Y%m%d')}&end={end.strftime('%Y%m%d')}&country={TEST_COUNTRY}",  # noqa
            status=500,
            json=kamereon_responses.MOCK_VEHICLE_HVAC_SESSIONS_INVALID_UPSTREAM,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.hvac_history(start, end)


def test_hvac_statistics_invalid_upstream() -> None:
    """Test vehicle hvac-history."""
    renault_vehicle = get_renault_vehicle()
    start = datetime(2020, 9, 1)
    end = datetime(2020, 10, 1)
    period = "month"
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/hvac-history?type={period}&start={start.strftime(PERIOD_FORMATS[period])}&end={end.strftime(PERIOD_FORMATS[period])}&country={TEST_COUNTRY}",  # noqa
            status=500,
            json=kamereon_responses.MOCK_VEHICLE_HVAC_HISTORY_INVALID_UPSTREAM,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.hvac_statistics(start, end, period)


def test_set_charge_mode() -> None:
    """Test vehicle actions/charge-mode."""
    renault_vehicle = get_renault_vehicle()
    charge_mode = ChargeMode.schedule_mode
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/actions/charge-mode?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLEACTIONS_CHARGE_MODE,
        )

        set_charge_mode = renault_vehicle.set_charge_mode(charge_mode)
        assert set_charge_mode


def test_set_charge_schedules() -> None:
    """Test vehicle actions/charge-schedule."""
    renault_vehicle = get_renault_vehicle()
    schedules = ChargeSchedules()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}/actions/charge-schedule?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLEACTIONS_CHARGE_SCHEDULE,
        )

        set_charge_schedules = renault_vehicle.set_charge_schedules(schedules)
        assert set_charge_schedules


def test_charge_start() -> None:
    """Test vehicle actions/charge-mode."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/actions/charging-start?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLEACTIONS_CHARGING_START,
        )

        charge_start = renault_vehicle.charge_start()
        assert charge_start


def test_ac_start() -> None:
    """Test vehicle actions/hvac-start."""
    renault_vehicle = get_renault_vehicle()
    start = datetime(2020, 9, 1)
    temperature = 23
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/actions/hvac-start?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLEACTIONS_HVAC_START,
        )

        ac_start = renault_vehicle.ac_start(start, temperature)
        assert ac_start


def test_ac_start_invalid_date() -> None:
    """Test vehicle actions/hvac-start."""
    renault_vehicle = get_renault_vehicle()
    start = datetime(2020, 9, 1)
    temperature = 23
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/actions/hvac-start?country={TEST_COUNTRY}",  # noqa
            status=400,
            json=kamereon_responses.MOCK_VEHICLEACTIONS_HVAC_START_INVALID_DATE,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            renault_vehicle.ac_start(start, temperature)


def test_cancel_ac() -> None:
    """Test vehicle actions/hvac-start(cancel)."""
    renault_vehicle = get_renault_vehicle()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}/actions/hvac-start?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_VEHICLEACTIONS_HVAC_START_CANCEL,
        )

        ac_start = renault_vehicle.cancel_ac()
        assert ac_start
