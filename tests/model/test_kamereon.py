"""Tests for Kamereon models."""
from typing import Any
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


def test_vehicle_data_response_attributes() -> None:
    """Test vehicle data response attributes."""
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


@pytest.mark.parametrize("filename", get_json_files(f"{FIXTURE_PATH}/vehicle_action"))
def test_vehicle_action_response(filename: str) -> None:
    """Test vehicle action response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        filename, model.KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the guid is hidden
    assert response.data.id == "guid"


def test_vehicle_action_response_attributes() -> None:
    """Test vehicle action response attributes."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/vehicle_action/hvac-start.start.json",
        model.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {
        "action": "start",
        "targetTemperature": 21.0,
    }
