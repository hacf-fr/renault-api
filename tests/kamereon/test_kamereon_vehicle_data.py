"""Tests for Kamereon models."""
from typing import cast

import pytest
from tests import fixtures

from renault_api.kamereon import enums
from renault_api.kamereon import models
from renault_api.kamereon import schemas


FIXTURE_PATH = "tests/fixtures/kamereon/vehicle_data"


@pytest.mark.parametrize("filename", fixtures.get_json_files(FIXTURE_PATH))
def test_vehicle_data_response(filename: str) -> None:
    """Test vehicle data response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the VIN is hidden
    assert response.data.id.startswith("VF1AAAA")


def test_battery_status_1() -> None:
    """Test vehicle data for battery-status.1.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/battery-status.1.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
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
        f"{FIXTURE_PATH}/battery-status.2.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
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


def test_cockpit_zoe() -> None:
    """Test vehicle data for cockpit.zoe.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/cockpit.zoe.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
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
        f"{FIXTURE_PATH}/cockpit.captur_ii.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
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


def test_charging_settings() -> None:
    """Test vehicle data for charging-settings.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/charging-settings.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
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
    assert len(vehicle_data.schedules) == 1

    schedule_data = vehicle_data.schedules[0]
    assert schedule_data.id == 1
    assert schedule_data.activated is True
    assert schedule_data.monday.startTime == "T12:00Z"
    assert schedule_data.monday.duration == 15
    assert schedule_data.tuesday.startTime == "T04:30Z"
    assert schedule_data.tuesday.duration == 420
    assert schedule_data.wednesday.startTime == "T22:30Z"
    assert schedule_data.wednesday.duration == 420
    assert schedule_data.thursday.startTime == "T22:00Z"
    assert schedule_data.thursday.duration == 420
    assert schedule_data.friday.startTime == "T12:15Z"
    assert schedule_data.friday.duration == 15
    assert schedule_data.saturday.startTime == "T12:30Z"
    assert schedule_data.saturday.duration == 30
    assert schedule_data.sunday.startTime == "T12:45Z"
    assert schedule_data.sunday.duration == 45


def test_location() -> None:
    """Test vehicle data for location.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/location.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
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


def test_charge_mode() -> None:
    """Test vehicle data for charge-mode.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/charge-mode.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {"chargeMode": "always"}

    vehicle_data = cast(
        models.KamereonVehicleChargeModeData,
        response.get_attributes(schemas.KamereonVehicleChargeModeDataSchema),
    )

    assert vehicle_data.chargeMode == "always"
    assert vehicle_data.get_charge_mode() == enums.ChargeMode.ALWAYS
