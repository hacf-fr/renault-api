"""Tests for Kamereon models."""

from typing import cast

import pytest

from tests import fixtures

from renault_api.kamereon import enums
from renault_api.kamereon import models
from renault_api.kamereon import schemas
from renault_api.kamereon.helpers import DAYS_OF_WEEK


@pytest.mark.parametrize(
    "filename",
    fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data"),
)
def test_vehicle_data_response(filename: str) -> None:
    """Test vehicle data response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the VIN is hidden
    if response.data and response.data.id:
        assert response.data.id.startswith(("VF1AAAA", "UU1AAAA"))


def test_battery_status_1() -> None:
    """Test vehicle data for battery-status.1.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/battery-status.1.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "timestamp": "2020-11-17T09:06:48+01:00",
        "batteryLevel": 50,
        "batteryAutonomy": 128,
        "batteryCapacity": 0,
        "batteryAvailableEnergy": 0,
        "plugStatus": 0,
        "chargingStatus": -1.0,
    }

    vehicle_data = cast(
        models.KamereonVehicleBatteryStatusData,
        response.get_attributes(schemas.KamereonVehicleBatteryStatusDataSchema),
    )

    assert vehicle_data.timestamp == "2020-11-17T09:06:48+01:00"
    assert vehicle_data.batteryLevel == 50
    assert vehicle_data.batteryTemperature is None
    assert vehicle_data.batteryAutonomy == 128
    assert vehicle_data.batteryCapacity == 0
    assert vehicle_data.batteryAvailableEnergy == 0
    assert vehicle_data.plugStatus == 0
    assert vehicle_data.chargingStatus == -1.0
    assert vehicle_data.chargingRemainingTime is None
    assert vehicle_data.chargingInstantaneousPower is None
    assert vehicle_data.get_plug_status() == enums.PlugState.UNPLUGGED
    assert vehicle_data.get_charging_status() == enums.ChargeState.CHARGE_ERROR


def test_battery_status_2() -> None:
    """Test vehicle data for battery-status.2.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/battery-status.2.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "timestamp": "2020-01-12T21:40:16Z",
        "batteryLevel": 60,
        "batteryTemperature": 20,
        "batteryAutonomy": 141,
        "batteryCapacity": 0,
        "batteryAvailableEnergy": 31,
        "plugStatus": 1,
        "chargingStatus": 1.0,
        "chargingRemainingTime": 145,
        "chargingInstantaneousPower": 27.0,
    }

    vehicle_data = cast(
        models.KamereonVehicleBatteryStatusData,
        response.get_attributes(schemas.KamereonVehicleBatteryStatusDataSchema),
    )

    assert vehicle_data.timestamp == "2020-01-12T21:40:16Z"
    assert vehicle_data.batteryLevel == 60
    assert vehicle_data.batteryTemperature == 20
    assert vehicle_data.batteryAutonomy == 141
    assert vehicle_data.batteryCapacity == 0
    assert vehicle_data.batteryAvailableEnergy == 31
    assert vehicle_data.plugStatus == 1
    assert vehicle_data.chargingStatus == 1.0
    assert vehicle_data.chargingRemainingTime == 145
    assert vehicle_data.chargingInstantaneousPower == 27.0
    assert vehicle_data.get_plug_status() == enums.PlugState.PLUGGED
    assert vehicle_data.get_charging_status() == enums.ChargeState.CHARGE_IN_PROGRESS


def test_tyre_pressure() -> None:
    """Test vehicle data for tyre pressure."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/pressure.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "flPressure": 2460,
        "frPressure": 2730,
        "rlPressure": 2790,
        "rrPressure": 2790,
        "flStatus": 0,
        "frStatus": 0,
        "rlStatus": 0,
        "rrStatus": 0,
    }


def test_cockpit_zoe() -> None:
    """Test vehicle data for cockpit.zoe.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/cockpit.zoe.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {"totalMileage": 49114.27}

    vehicle_data = cast(
        models.KamereonVehicleCockpitData,
        response.get_attributes(schemas.KamereonVehicleCockpitDataSchema),
    )

    assert vehicle_data.totalMileage == 49114.27
    assert vehicle_data.fuelAutonomy is None
    assert vehicle_data.fuelQuantity is None


def test_cockpit_captur_ii() -> None:
    """Test vehicle data for cockpit.captur_ii.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/cockpit.captur_ii.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "fuelAutonomy": 35.0,
        "fuelQuantity": 3.0,
        "totalMileage": 5566.78,
    }

    vehicle_data = cast(
        models.KamereonVehicleCockpitData,
        response.get_attributes(schemas.KamereonVehicleCockpitDataSchema),
    )

    assert vehicle_data.totalMileage == 5566.78
    assert vehicle_data.fuelAutonomy == 35.0
    assert vehicle_data.fuelQuantity == 3.0


def test_charging_settings_single() -> None:
    """Test vehicle data for charging-settings.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/charging-settings.single.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "mode": "scheduled",
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": {"startTime": "T12:00Z", "duration": 15},
                "tuesday": {"startTime": "T04:30Z", "duration": 420},
                "wednesday": {"startTime": "T22:30Z", "duration": 420},
                "thursday": {"startTime": "T22:00Z", "duration": 420},
                "friday": {"startTime": "T12:15Z", "duration": 15},
                "saturday": {"startTime": "T12:30Z", "duration": 30},
                "sunday": {"startTime": "T12:45Z", "duration": 45},
            }
        ],
    }

    vehicle_data = cast(
        models.KamereonVehicleChargingSettingsData,
        response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
    )

    assert vehicle_data.mode == "scheduled"
    assert vehicle_data.schedules is not None
    assert len(vehicle_data.schedules) == 1

    schedule_data = vehicle_data.schedules[0]
    assert schedule_data.id == 1
    assert schedule_data.activated is True
    assert schedule_data.monday is not None
    assert schedule_data.monday.startTime == "T12:00Z"
    assert schedule_data.monday.duration == 15
    assert schedule_data.tuesday is not None
    assert schedule_data.tuesday.startTime == "T04:30Z"
    assert schedule_data.tuesday.duration == 420
    assert schedule_data.wednesday is not None
    assert schedule_data.wednesday.startTime == "T22:30Z"
    assert schedule_data.wednesday.duration == 420
    assert schedule_data.thursday is not None
    assert schedule_data.thursday.startTime == "T22:00Z"
    assert schedule_data.thursday.duration == 420
    assert schedule_data.friday is not None
    assert schedule_data.friday.startTime == "T12:15Z"
    assert schedule_data.friday.duration == 15
    assert schedule_data.saturday is not None
    assert schedule_data.saturday.startTime == "T12:30Z"
    assert schedule_data.saturday.duration == 30
    assert schedule_data.sunday is not None
    assert schedule_data.sunday.startTime == "T12:45Z"
    assert schedule_data.sunday.duration == 45


def test_charging_settings_multi() -> None:
    """Test vehicle data for charging-settings.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/charging-settings.multi.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "mode": "scheduled",
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": {"startTime": "T00:00Z", "duration": 450},
                "tuesday": {"startTime": "T00:00Z", "duration": 450},
                "wednesday": {"startTime": "T00:00Z", "duration": 450},
                "thursday": {"startTime": "T00:00Z", "duration": 450},
                "friday": {"startTime": "T00:00Z", "duration": 450},
                "saturday": {"startTime": "T00:00Z", "duration": 450},
                "sunday": {"startTime": "T00:00Z", "duration": 450},
            },
            {
                "id": 2,
                "activated": True,
                "monday": {"startTime": "T23:30Z", "duration": 15},
                "tuesday": {"startTime": "T23:30Z", "duration": 15},
                "wednesday": {"startTime": "T23:30Z", "duration": 15},
                "thursday": {"startTime": "T23:30Z", "duration": 15},
                "friday": {"startTime": "T23:30Z", "duration": 15},
                "saturday": {"startTime": "T23:30Z", "duration": 15},
                "sunday": {"startTime": "T23:30Z", "duration": 15},
            },
            {"id": 3, "activated": False},
            {"id": 4, "activated": False},
            {"id": 5, "activated": False},
        ],
    }

    vehicle_data = cast(
        models.KamereonVehicleChargingSettingsData,
        response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
    )

    assert vehicle_data.mode == "scheduled"
    assert vehicle_data.schedules is not None
    assert len(vehicle_data.schedules) == 5

    schedule_data = vehicle_data.schedules[0]
    assert schedule_data.id == 1
    assert schedule_data.activated is True
    assert schedule_data.monday is not None
    assert schedule_data.monday.startTime == "T00:00Z"
    assert schedule_data.monday.duration == 450
    assert schedule_data.tuesday is not None
    assert schedule_data.tuesday.startTime == "T00:00Z"
    assert schedule_data.tuesday.duration == 450
    assert schedule_data.wednesday is not None
    assert schedule_data.wednesday.startTime == "T00:00Z"
    assert schedule_data.wednesday.duration == 450
    assert schedule_data.thursday is not None
    assert schedule_data.thursday.startTime == "T00:00Z"
    assert schedule_data.thursday.duration == 450
    assert schedule_data.friday is not None
    assert schedule_data.friday.startTime == "T00:00Z"
    assert schedule_data.friday.duration == 450
    assert schedule_data.saturday is not None
    assert schedule_data.saturday.startTime == "T00:00Z"
    assert schedule_data.saturday.duration == 450
    assert schedule_data.sunday is not None
    assert schedule_data.sunday.startTime == "T00:00Z"
    assert schedule_data.sunday.duration == 450


def test_location_v1() -> None:
    """Test vehicle data for location.1.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/location.1.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "gpsLatitude": 48.1234567,
        "gpsLongitude": 11.1234567,
        "lastUpdateTime": "2020-02-18T16:58:38Z",
    }

    vehicle_data = cast(
        models.KamereonVehicleLocationData,
        response.get_attributes(schemas.KamereonVehicleLocationDataSchema),
    )

    assert vehicle_data.gpsLatitude == 48.1234567
    assert vehicle_data.gpsLongitude == 11.1234567
    assert vehicle_data.lastUpdateTime == "2020-02-18T16:58:38Z"


def test_location_v2() -> None:
    """Test vehicle data for location.2.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/location.2.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "gpsDirection": None,
        "gpsLatitude": 48.1234567,
        "gpsLongitude": 11.1234567,
        "lastUpdateTime": "2020-02-18T16:58:38Z",
    }

    vehicle_data = cast(
        models.KamereonVehicleLocationData,
        response.get_attributes(schemas.KamereonVehicleLocationDataSchema),
    )

    assert vehicle_data.gpsLatitude == 48.1234567
    assert vehicle_data.gpsLongitude == 11.1234567
    assert vehicle_data.lastUpdateTime == "2020-02-18T16:58:38Z"


def test_lock_status_locked() -> None:
    """Test lock-status for lock-status.1.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/lock-status.1.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "lockStatus": "locked",
        "doorStatusRearLeft": "closed",
        "doorStatusRearRight": "closed",
        "doorStatusDriver": "closed",
        "doorStatusPassenger": "closed",
        "hatchStatus": "closed",
        "lastUpdateTime": "2022-02-02T13:51:13Z",
    }

    vehicle_data = cast(
        models.KamereonVehicleLockStatusData,
        response.get_attributes(schemas.KamereonVehicleLockStatusDataSchema),
    )

    assert vehicle_data.lockStatus == "locked"
    assert vehicle_data.doorStatusRearLeft == "closed"
    assert vehicle_data.doorStatusRearRight == "closed"
    assert vehicle_data.doorStatusDriver == "closed"
    assert vehicle_data.doorStatusPassenger == "closed"
    assert vehicle_data.hatchStatus == "closed"
    assert vehicle_data.lastUpdateTime == "2022-02-02T13:51:13Z"


def test_lock_status_unlocked() -> None:
    """Test lock-status for lock-status.2.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/lock-status.2.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "lockStatus": "unlocked",
        "doorStatusRearLeft": "closed",
        "doorStatusRearRight": "closed",
        "doorStatusDriver": "closed",
        "doorStatusPassenger": "closed",
        "hatchStatus": "closed",
        "lastUpdateTime": "2022-02-02T13:51:13Z",
    }

    vehicle_data = cast(
        models.KamereonVehicleLockStatusData,
        response.get_attributes(schemas.KamereonVehicleLockStatusDataSchema),
    )

    assert vehicle_data.lockStatus == "unlocked"
    assert vehicle_data.doorStatusRearLeft == "closed"
    assert vehicle_data.doorStatusRearRight == "closed"
    assert vehicle_data.doorStatusDriver == "closed"
    assert vehicle_data.doorStatusPassenger == "closed"
    assert vehicle_data.hatchStatus == "closed"
    assert vehicle_data.lastUpdateTime == "2022-02-02T13:51:13Z"


def test_res_state_stopped() -> None:
    """Test res-state for res-state.1.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/res-state.1.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "details": "Stopped, ready for RES",
        "code": "10",
    }

    vehicle_data = cast(
        models.KamereonVehicleResStateData,
        response.get_attributes(schemas.KamereonVehicleResStateDataSchema),
    )

    assert vehicle_data.details == "Stopped, ready for RES"
    assert vehicle_data.code == "10"


def test_res_state_running() -> None:
    """Test res-state for res-state.2.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/res-state.2.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "details": "Running",
        "code": "42",
    }

    vehicle_data = cast(
        models.KamereonVehicleResStateData,
        response.get_attributes(schemas.KamereonVehicleResStateDataSchema),
    )

    assert vehicle_data.details == "Running"
    assert vehicle_data.code == "42"


def test_charge_mode() -> None:
    """Test vehicle data for charge-mode.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/charge-mode.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {"chargeMode": "always"}

    vehicle_data = cast(
        models.KamereonVehicleChargeModeData,
        response.get_attributes(schemas.KamereonVehicleChargeModeDataSchema),
    )

    assert vehicle_data.chargeMode == "always"


def test_hvac_settings_mode() -> None:
    """Test vehicle data with hvac settings for mode."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/hvac-settings.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()

    vehicle_data = cast(
        models.KamereonVehicleHvacSettingsData,
        response.get_attributes(schemas.KamereonVehicleHvacSettingsDataSchema),
    )

    assert vehicle_data.mode == "scheduled"


def test_hvac_settings_schedule() -> None:
    """Test vehicle data with hvac schedule entries."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/hvac-settings.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()

    vehicle_data = cast(
        models.KamereonVehicleHvacSettingsData,
        response.get_attributes(schemas.KamereonVehicleHvacSettingsDataSchema),
    )

    assert vehicle_data.mode == "scheduled"
    assert vehicle_data.schedules is not None
    assert vehicle_data.schedules[1].id == 2
    assert vehicle_data.schedules[1].wednesday is not None
    assert vehicle_data.schedules[1].wednesday.readyAtTime == "T15:15Z"
    assert vehicle_data.schedules[1].friday is not None
    assert vehicle_data.schedules[1].friday.readyAtTime == "T15:15Z"
    assert vehicle_data.schedules[1].monday is None

    for i in [0, 2, 3, 4]:
        assert vehicle_data.schedules[i].id == i + 1
        for day in DAYS_OF_WEEK:
            assert vehicle_data.schedules[i].__dict__.get(day) is None


def test_no_data() -> None:
    """Test missing vehicle data."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/no_data.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data == {"id": "VF1AAAA", "type": "ChargeMode"}

    vehicle_data = cast(
        models.KamereonVehicleCockpitData,
        response.get_attributes(schemas.KamereonVehicleCockpitDataSchema),
    )

    assert vehicle_data.totalMileage is None
    assert vehicle_data.fuelAutonomy is None
    assert vehicle_data.fuelQuantity is None
