"""Tests for Kamereon models."""
from copy import deepcopy
from os import path

import pytest
from tests import fixtures
from tests.const import TO_REDACT

from .test_kamereon_vehicles import EXPECTED_SPECS
from renault_api.kamereon import models
from renault_api.kamereon import schemas
from renault_api.kamereon.enums import AssetPictureSize


@pytest.mark.parametrize(
    "filename",
    fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_details"),
)
def test_vehicle_details_response(filename: str) -> None:
    """Test vehicle_details response."""
    vehicle_details: models.KamereonVehicleDetailsResponse = (
        fixtures.get_file_content_as_schema(
            filename, schemas.KamereonVehicleDetailsResponseSchema
        )
    )
    vehicle_details.raise_for_error_code()
    fixtures.ensure_redacted(vehicle_details.raw_data, [*TO_REDACT, "id"])

    if path.basename(filename) in EXPECTED_SPECS:
        expected_specs = deepcopy(EXPECTED_SPECS[path.basename(filename)])
        power_in_watts = vehicle_details.reports_charging_power_in_watts()
        generated_specs = {
            "reports_charging_power_in_watts": power_in_watts,
            "uses_electricity": vehicle_details.uses_electricity(),
            "uses_fuel": vehicle_details.uses_fuel(),
            "supports-hvac-status": vehicle_details.supports_endpoint("hvac-status"),
            "supports-location": vehicle_details.supports_endpoint("location"),
            "charge-uses-kcm": vehicle_details.controls_action_via_kcm("charge"),
            "get_brand_label": vehicle_details.get_brand_label(),
            "get_energy_code": vehicle_details.get_energy_code(),
            "get_model_code": vehicle_details.get_model_code(),
            "get_model_label": vehicle_details.get_model_label(),
            "get_picture_large": vehicle_details.get_picture(AssetPictureSize.LARGE),
            "get_picture_small": vehicle_details.get_picture(AssetPictureSize.SMALL),
        }
        assert expected_specs == generated_specs
