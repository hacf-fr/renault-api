"""Tests for Kamereon models."""
from typing import Any
from typing import cast
from typing import Type

import pytest
from marshmallow.schema import Schema
from tests import get_json_files

from renault_api.model import kamereon as model


FIXTURE_PATH = "tests/fixtures/kamereon/"


def get_response_content(path: str, schema: Type[Schema]) -> Any:
    """Read fixture text file as string."""
    with open(path, "r") as file:
        content = file.read()
    return schema.loads(content)


@pytest.mark.parametrize("filename", get_json_files(f"{FIXTURE_PATH}/vehicle_data"))
def test_vehicle_data_response(filename: str) -> None:
    """Test vehicle data response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        filename, model.KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the VIN is hidden
    assert response.data.id.startswith("VF1AAAAA555777")


def test_battery_status_1() -> None:
    """Test vehicle data for battery-status.1.json."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}vehicle_data/battery-status.1.json",
        model.KamereonVehicleDataResponseSchema,
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
        model.KamereonVehicleBatteryStatusData,
        response.get_attributes(model.KamereonVehicleBatteryStatusDataSchema),
    )

    assert vehicle_data.timestamp == "2020-11-17T09:06:48+01:00"
    assert vehicle_data.batteryLevel == 50
    assert vehicle_data.batteryTemperature is None
    assert vehicle_data.batteryAutonomy == 128
    assert vehicle_data.batteryCapacity == 0
    assert vehicle_data.batteryAvailableEnergy == 0
    assert vehicle_data.plugStatus == 0
    assert vehicle_data.chargingStatus == -1.0
    assert vehicle_data.get_plug_status() == model.PlugState.UNPLUGGED
    assert vehicle_data.get_charging_status() == model.ChargeState.CHARGE_ERROR


def test_battery_status_2() -> None:
    """Test vehicle data for battery-status.2.json."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}vehicle_data/battery-status.2.json",
        model.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {
        "timestamp": "2020-11-09T07:41:49+01:00",
        "batteryLevel": 34,
        "batteryTemperature": 10,
        "batteryAutonomy": 88,
        "batteryCapacity": 0,
        "batteryAvailableEnergy": 0,
        "plugStatus": 0,
        "chargingStatus": -1.0,
    }

    vehicle_data = cast(
        model.KamereonVehicleBatteryStatusData,
        response.get_attributes(model.KamereonVehicleBatteryStatusDataSchema),
    )

    assert vehicle_data.timestamp == "2020-11-09T07:41:49+01:00"
    assert vehicle_data.batteryLevel == 34
    assert vehicle_data.batteryTemperature == 10
    assert vehicle_data.batteryAutonomy == 88
    assert vehicle_data.batteryCapacity == 0
    assert vehicle_data.batteryAvailableEnergy == 0
    assert vehicle_data.plugStatus == 0
    assert vehicle_data.chargingStatus == -1.0
    assert vehicle_data.get_plug_status() == model.PlugState.UNPLUGGED
    assert vehicle_data.get_charging_status() == model.ChargeState.CHARGE_ERROR


def test_cockpit_zoe() -> None:
    """Test vehicle data for cockpit.zoe.json."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}vehicle_data/cockpit.zoe.json",
        model.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {"totalMileage": 49114.27}

    vehicle_data = cast(
        model.KamereonVehicleCockpitData,
        response.get_attributes(model.KamereonVehicleCockpitDataSchema),
    )

    assert vehicle_data.totalMileage == 49114.27
    assert vehicle_data.fuelAutonomy is None
    assert vehicle_data.fuelQuantity is None


def test_cockpit_captur_ii() -> None:
    """Test vehicle data for cockpit.captur_ii.json."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}vehicle_data/cockpit.captur_ii.json",
        model.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {
        "fuelAutonomy": 35.0,
        "fuelQuantity": 3.0,
        "totalMileage": 5566.78,
    }

    vehicle_data = cast(
        model.KamereonVehicleCockpitData,
        response.get_attributes(model.KamereonVehicleCockpitDataSchema),
    )

    assert vehicle_data.totalMileage == 5566.78
    assert vehicle_data.fuelAutonomy == 35.0
    assert vehicle_data.fuelQuantity == 3.0
