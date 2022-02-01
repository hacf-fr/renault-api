"""Tests for Kamereon models."""
import os
from copy import deepcopy
from typing import cast

import pytest
from tests import fixtures
from tests.const import TO_REDACT

from .test_kamereon_vehicles import EXPECTED_SPECS
from renault_api.kamereon import models
from renault_api.kamereon import schemas


@pytest.mark.parametrize(
    "filename",
    fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_gateway"),
)
def test_vehicles_response(filename: str) -> None:
    """Test vehicles list response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    fixtures.ensure_redacted(response.raw_data, [*TO_REDACT, "id"])
    assert response.data
    assert response.data.attributes
    fixtures.ensure_redacted(response.data.attributes)

    vehicle_data = cast(
        models.KamereonVehicleCarAdapterData,
        response.get_attributes(schemas.KamereonVehicleCarAdapterDataSchema),
    )

    if os.path.basename(filename) in EXPECTED_SPECS:
        expected_specs = deepcopy(EXPECTED_SPECS[os.path.basename(filename)])
        del expected_specs["get_brand_label"]
        del expected_specs["get_energy_code"]
        del expected_specs["get_model_code"]
        del expected_specs["get_model_label"]
        power_in_watts = vehicle_data.reports_charging_power_in_watts()
        generated_specs = {
            "reports_charging_power_in_watts": power_in_watts,
            "uses_electricity": vehicle_data.uses_electricity(),
            "uses_fuel": vehicle_data.uses_fuel(),
            "supports-hvac-status": vehicle_data.supports_endpoint("hvac-status"),
            "supports-location": vehicle_data.supports_endpoint("location"),
            "charging-endpoints-uses-kcm": vehicle_data.uses_endpoint_via_kcm(
                "pause-resume"
            ),
        }
        assert expected_specs == generated_specs
