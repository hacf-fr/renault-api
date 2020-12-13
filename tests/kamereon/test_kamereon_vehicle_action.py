"""Tests for Kamereon models."""
import pytest
from tests import fixtures

from renault_api.kamereon import models
from renault_api.kamereon import schemas


FIXTURE_PATH = "tests/fixtures/kamereon/vehicle_action"


@pytest.mark.parametrize("filename", fixtures.get_json_files(FIXTURE_PATH))
def test_vehicle_action_response(filename: str) -> None:
    """Test vehicle action response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the guid is hidden
    assert response.data.id == "guid"


def test_vehicle_action_response_attributes() -> None:
    """Test vehicle action response attributes."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/hvac-start.start.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {
        "action": "start",
        "targetTemperature": 21.0,
    }
