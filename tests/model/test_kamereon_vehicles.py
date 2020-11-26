"""Tests for Kamereon models."""
import pytest
from tests import get_json_files
from tests import get_response_content

from renault_api.model import kamereon as model


FIXTURE_PATH = "tests/fixtures/kamereon/vehicles"


@pytest.mark.parametrize("filename", get_json_files(FIXTURE_PATH))
def test_vehicles_response(filename: str) -> None:
    """Test vehicles list response."""
    response: model.KamereonVehiclesResponse = get_response_content(
        filename, model.KamereonVehiclesResponseSchema
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
