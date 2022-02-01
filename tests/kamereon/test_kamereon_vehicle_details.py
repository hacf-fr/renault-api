"""Tests for Kamereon models."""
import pytest
from tests import fixtures
from tests.const import TO_REDACT

from renault_api.kamereon import models
from renault_api.kamereon import schemas


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
