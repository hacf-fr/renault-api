"""Tests for RenaultClient."""
import os
from typing import Any
from typing import Type

import pytest
from marshmallow.schema import Schema

from renault_api.exceptions import KamereonResponseException
from renault_api.model.kamereon import KamereonPersonResponse
from renault_api.model.kamereon import KamereonPersonResponseSchema
from renault_api.model.kamereon import KamereonVehicleDataResponse
from renault_api.model.kamereon import KamereonVehicleDataResponseSchema
from renault_api.model.kamereon import KamereonVehiclesResponse
from renault_api.model.kamereon import KamereonVehiclesResponseSchema


def get_response_content(path: str, schema: Type[Schema]) -> Any:
    """Read fixture text file as string."""
    with open(f"tests/fixtures/kamereon/{path}", "r") as file:
        content = file.read()
    return schema.loads(content)


def test_person_response() -> None:
    """Test login response."""
    response: KamereonPersonResponse = get_response_content(
        "person.json", KamereonPersonResponseSchema
    )
    response.raise_for_error_code()
    assert response.accounts[0].accountId == "account-id-1"
    assert response.accounts[0].accountType == "MYRENAULT"
    assert response.accounts[0].accountStatus == "ACTIVE"

    assert response.accounts[1].accountId == "account-id-2"
    assert response.accounts[1].accountType == "SFDC"
    assert response.accounts[1].accountStatus == "ACTIVE"


def test_vehicles_response() -> None:
    """Test login response."""
    directory = "tests/fixtures/kamereon/vehicles"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        response: KamereonVehiclesResponse = get_response_content(
            f"vehicles/{filename}", KamereonVehiclesResponseSchema
        )
        response.raise_for_error_code()
        assert response.accountId == "account-id-1"
        for vehicle_link in response.vehicleLinks:
            assert vehicle_link.vin == "VF1AAAAA555777999"


def test_vehicle_data_response() -> None:
    """Test login response."""
    directory = "tests/fixtures/kamereon/vehicle_data"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        response: KamereonVehicleDataResponse = get_response_content(
            f"vehicle_data/{filename}", KamereonVehicleDataResponseSchema
        )
        response.raise_for_error_code()
        assert response.data.id == "VF1AAAAA555777999"


def test_vehicle_data_response_attributes() -> None:
    """Test login response."""
    response: KamereonVehicleDataResponse = get_response_content(
        "vehicle_data/battery-status.1.json", KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    assert response.data.attributes == {
        "timestamp": "2020-11-17T09:06:48+01:00",
        "batteryLevel": 50,
        "batteryAutonomy": 128,
        "batteryCapacity": 0,
        "batteryAvailableEnergy": 0,
        "plugStatus": 0,
        "chargingStatus": -1.0,
    }


def test_vehicle_action_response() -> None:
    """Test login response."""
    directory = "tests/fixtures/kamereon/vehicle_action"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        response: KamereonVehicleDataResponse = get_response_content(
            f"vehicle_action/{filename}", KamereonVehicleDataResponseSchema
        )
        response.raise_for_error_code()
        assert response.data.id == "guid"


def test_vehicle_action_response_attributes() -> None:
    """Test login response."""
    response: KamereonVehicleDataResponse = get_response_content(
        "vehicle_action/hvac-start.start.json", KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    assert response.data.attributes == {"action": "start", "targetTemperature": 21.0}


def test_vehicle_error_response() -> None:
    """Test login response."""
    directory = "tests/fixtures/kamereon/vehicle_error"
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        response: KamereonVehicleDataResponse = get_response_content(
            f"vehicle_error/{filename}", KamereonVehicleDataResponseSchema
        )
        with pytest.raises(KamereonResponseException):
            response.raise_for_error_code()
            assert response.errors is not None


def test_vehicle_error_quota_limit() -> None:
    """Test login response."""
    response: KamereonVehicleDataResponse = get_response_content(
        "vehicle_error/quota_limit.json", KamereonVehicleDataResponseSchema
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
        assert excinfo.value.error_code == "err.func.wired.overloaded"
        assert excinfo.value.error_details == "You have reached your quota limit"
