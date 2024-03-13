"""Tests for Kamereon models."""
import json
import os

import pytest

from tests import fixtures

from renault_api.kamereon import models
from renault_api.kamereon import schemas
from renault_api.kamereon.enums import AssetPictureSize

EXPECTED_SPECS = json.loads(
    fixtures.get_file_content(f"{fixtures.KAMEREON_FIXTURE_PATH}/expected_specs.json")
)


@pytest.mark.parametrize(
    "filename", fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicles")
)
def test_vehicles_response(filename: str) -> None:
    """Test vehicles list response."""
    response: models.KamereonVehiclesResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehiclesResponseSchema
    )
    response.raise_for_error_code()
    fixtures.ensure_redacted(response.raw_data)

    assert response.vehicleLinks is not None
    for vehicle_link in response.vehicleLinks:
        fixtures.ensure_redacted(vehicle_link.raw_data)

        vehicle_details = vehicle_link.vehicleDetails
        assert vehicle_details
        fixtures.ensure_redacted(vehicle_details.raw_data)

        if os.path.basename(filename) in EXPECTED_SPECS:
            power_in_watts = vehicle_details.reports_charging_power_in_watts()
            generated_specs = {
                "get_brand_label": vehicle_details.get_brand_label(),
                "get_energy_code": vehicle_details.get_energy_code(),
                "get_model_code": vehicle_details.get_model_code(),
                "get_model_label": vehicle_details.get_model_label(),
                "get_picture_small": vehicle_details.get_picture(
                    AssetPictureSize.SMALL
                ),
                "get_picture_large": vehicle_details.get_picture(
                    AssetPictureSize.LARGE
                ),
                "reports_charging_power_in_watts": power_in_watts,
                "uses_electricity": vehicle_details.uses_electricity(),
                "uses_fuel": vehicle_details.uses_fuel(),
                "supports-hvac-status": vehicle_details.supports_endpoint(
                    "hvac-status"
                ),
                "supports-location": vehicle_details.supports_endpoint("location"),
                "charge-uses-kcm": vehicle_details.controls_action_via_kcm("charge"),
            }
            assert EXPECTED_SPECS[os.path.basename(filename)] == generated_specs
