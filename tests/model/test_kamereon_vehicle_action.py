"""Tests for Kamereon models."""
import pytest
from tests import get_json_files
from tests import get_response_content

from renault_api.model import kamereon as model


FIXTURE_PATH = "tests/fixtures/kamereon/vehicle_action"


@pytest.mark.parametrize("filename", get_json_files(FIXTURE_PATH))
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
        f"{FIXTURE_PATH}/hvac-start.start.json",
        model.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data.raw_data["attributes"] == {
        "action": "start",
        "targetTemperature": 21.0,
    }
