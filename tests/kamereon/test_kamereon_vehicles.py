"""Tests for Kamereon models."""
import pytest
from tests import get_json_files
from tests import get_response_content

from renault_api.kamereon import enums
from renault_api.kamereon import models
from renault_api.kamereon import schemas


FIXTURE_PATH = "tests/fixtures/kamereon/vehicles"


@pytest.mark.parametrize("filename", get_json_files(FIXTURE_PATH))
def test_vehicles_response(filename: str) -> None:
    """Test vehicles list response."""
    response: models.KamereonVehiclesResponse = get_response_content(
        filename, schemas.KamereonVehiclesResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the account id is hidden
    assert response.accountId.startswith("account-id")
    for vehicle_link in response.vehicleLinks:
        # Ensure the VIN and RegistrationNumber are hidden
        assert vehicle_link.vin
        assert vehicle_link.vin.startswith("VF1AAAA")

        vehicle_details = vehicle_link.vehicleDetails
        assert vehicle_details
        assert vehicle_details.vin
        assert vehicle_details.vin.startswith("VF1AAAA")
        assert vehicle_details.registrationNumber
        assert vehicle_details.registrationNumber.startswith("REG-")

        # Ensure the methods work
        assert vehicle_details.get_brand_label()
        assert vehicle_details.get_energy_code()
        assert vehicle_details.get_model_code()
        assert vehicle_details.get_model_label()


def test_zoe40_1() -> None:
    """Test vehicle details for zoe_40.1.json."""
    response: models.KamereonVehiclesResponse = get_response_content(
        f"{FIXTURE_PATH}/zoe_40.1.json", schemas.KamereonVehiclesResponseSchema
    )
    vehicle_details = response.vehicleLinks[0].vehicleDetails
    assert vehicle_details
    assert vehicle_details.get_brand_label() == "RENAULT"
    assert vehicle_details.get_energy_code() == enums.EnergyCode.ELECTRIQUE
    assert vehicle_details.get_model_code() == "X101VE"
    assert vehicle_details.get_model_label() == "ZOE"
    assert vehicle_details.reports_charging_power_in_watts()


def test_zoe40_2() -> None:
    """Test vehicle details for zoe_40.2.json."""
    response: models.KamereonVehiclesResponse = get_response_content(
        f"{FIXTURE_PATH}/zoe_40.2.json", schemas.KamereonVehiclesResponseSchema
    )
    vehicle_details = response.vehicleLinks[0].vehicleDetails
    assert vehicle_details
    assert vehicle_details.get_brand_label() == "RENAULT"
    assert vehicle_details.get_energy_code() == enums.EnergyCode.ELECTRIQUE
    assert vehicle_details.get_model_code() == "X101VE"
    assert vehicle_details.get_model_label() == "ZOE"
    assert vehicle_details.reports_charging_power_in_watts()


def test_capturii_1() -> None:
    """Test vehicle details for captur_ii.1.json."""
    response: models.KamereonVehiclesResponse = get_response_content(
        f"{FIXTURE_PATH}/captur_ii.1.json", schemas.KamereonVehiclesResponseSchema
    )
    vehicle_details = response.vehicleLinks[0].vehicleDetails
    assert vehicle_details
    assert vehicle_details.get_brand_label() == "RENAULT"
    assert vehicle_details.get_energy_code() == enums.EnergyCode.ESSENCE
    assert vehicle_details.get_model_code() == "XJB1SU"
    assert vehicle_details.get_model_label() == "CAPTUR II"
    assert not vehicle_details.reports_charging_power_in_watts()
