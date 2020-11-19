"""Tests for RenaultClient."""
from typing import Any
from typing import Type

import pytest
from marshmallow.schema import Schema
from tests import get_json_files

from renault_api.exceptions import KamereonResponseException
from renault_api.model.kamereon import KamereonPersonResponse
from renault_api.model.kamereon import KamereonPersonResponseSchema
from renault_api.model.kamereon import KamereonVehicleDataResponse
from renault_api.model.kamereon import KamereonVehicleDataResponseSchema
from renault_api.model.kamereon import KamereonVehiclesResponse
from renault_api.model.kamereon import KamereonVehiclesResponseSchema


FIXTURE_PATH = "tests/fixtures/kamereon/"


def get_response_content(path: str, schema: Type[Schema]) -> Any:
    """Read fixture text file as string."""
    with open(path, "r") as file:
        content = file.read()
    return schema.loads(content)


def test_person_response() -> None:
    """Test person details response."""
    response: KamereonPersonResponse = get_response_content(
        f"{FIXTURE_PATH}/person.json", KamereonPersonResponseSchema
    )
    response.raise_for_error_code()
    assert response.accounts[0].accountId == "account-id-1"
    assert response.accounts[0].accountType == "MYRENAULT"
    assert response.accounts[0].accountStatus == "ACTIVE"

    assert response.accounts[1].accountId == "account-id-2"
    assert response.accounts[1].accountType == "SFDC"
    assert response.accounts[1].accountStatus == "ACTIVE"


@pytest.mark.parametrize("filename", get_json_files(f"{FIXTURE_PATH}/vehicles"))
def test_vehicles_response(filename: str) -> None:
    """Test vehicles list response."""
    response: KamereonVehiclesResponse = get_response_content(
        filename, KamereonVehiclesResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the account id is hidden
    assert response.accountId.startswith("account-id")
    for vehicle_link in response.vehicleLinks:
        # Ensure the VIN is hidden
        assert vehicle_link.vin.startswith("VF1AAAAA555777")
        vehicle_details = vehicle_link.raw_data["vehicleDetails"]
        assert vehicle_details["vin"].startswith("VF1AAAAA555777")
        assert vehicle_details["registrationNumber"].startswith("REG-NUMBER")


@pytest.mark.parametrize("filename", get_json_files(f"{FIXTURE_PATH}/vehicle_data"))
def test_vehicle_data_response(filename: str) -> None:
    """Test vehicle data response."""
    response: KamereonVehicleDataResponse = get_response_content(
        filename, KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the VIN is hidden
    assert response.data.id.startswith("VF1AAAAA555777")


def test_vehicle_data_response_attributes() -> None:
    """Test vehicle data response attributes."""
    response: KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}vehicle_data/battery-status.1.json",
        KamereonVehicleDataResponseSchema,
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
    response: KamereonVehicleDataResponse = get_response_content(
        filename, KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the guid is hidden
    assert response.data.id == "guid"


def test_vehicle_action_response_attributes() -> None:
    """Test vehicle action response attributes."""
    response: KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/vehicle_action/hvac-start.start.json",
        KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {
        "action": "start",
        "targetTemperature": 21.0,
    }


@pytest.mark.parametrize("filename", get_json_files(f"{FIXTURE_PATH}/error"))
def test_vehicle_error_response(filename: str) -> None:
    """Test vehicle error response."""
    response: KamereonVehicleDataResponse = get_response_content(
        filename, KamereonVehicleDataResponseSchema
    )
    with pytest.raises(KamereonResponseException):
        response.raise_for_error_code()
    assert response.errors is not None


def test_vehicle_error_quota_limit() -> None:
    """Test vehicle quota_limit response."""
    response: KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/error/quota_limit.json",
        KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.wired.overloaded"
    assert excinfo.value.error_details == "You have reached your quota limit"


def test_vehicle_error_invalid_date() -> None:
    """Test vehicle invalid_date response."""
    response: KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/error/invalid_date.json",
        KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.400"
    assert (
        excinfo.value.error_details
        == "/data/attributes/startDateTime must be a future date"
    )


def test_vehicle_error_invalid_upstream() -> None:
    """Test vehicle invalid_upstream response."""
    response: KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/error/invalid_upstream.json",
        KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.tech.500"
    assert (
        excinfo.value.error_details
        == "Invalid response from the upstream server (The request sent to the GDC"
        " is erroneous) ; 502 Bad Gateway"
    )


def test_vehicle_error_not_supported() -> None:
    """Test vehicle not_supported response."""
    response: KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/error/not_supported.json",
        KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.tech.501"
    assert (
        excinfo.value.error_details
        == "This feature is not technically supported by this gateway"
    )


def test_vehicle_error_resource_not_found() -> None:
    """Test vehicle not_supported response."""
    response: KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/error/resource_not_found.json",
        KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.wired.notFound"
    assert excinfo.value.error_details == "Resource not found"
