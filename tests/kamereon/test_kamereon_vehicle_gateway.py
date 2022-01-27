"""Tests for Kamereon models."""
import pytest
from tests import fixtures
from tests.const import TO_REDACT

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
    fixtures.ensure_redacted(response.data.attributes)
