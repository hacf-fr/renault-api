"""Tests for Kamereon models."""
import pytest
from tests import fixtures

from renault_api.kamereon import exceptions
from renault_api.kamereon import models
from renault_api.kamereon import schemas


FIXTURE_PATH = "tests/fixtures/kamereon/error"


@pytest.mark.parametrize("filename", fixtures.get_json_files(FIXTURE_PATH))
def test_vehicle_error_response(filename: str) -> None:
    """Test vehicle error response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehicleDataResponseSchema
    )
    with pytest.raises(exceptions.KamereonResponseException):
        response.raise_for_error_code()
    assert response.errors is not None


def test_vehicle_error_quota_limit() -> None:
    """Test vehicle quota_limit response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/quota_limit.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(exceptions.QuotaLimitException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.wired.overloaded"
    assert excinfo.value.error_details == "You have reached your quota limit"


def test_vehicle_error_invalid_date() -> None:
    """Test vehicle invalid_date response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/invalid_date.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(exceptions.InvalidInputException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.400"
    assert (
        excinfo.value.error_details
        == "/data/attributes/startDateTime must be a future date"
    )


def test_vehicle_error_invalid_upstream() -> None:
    """Test vehicle invalid_upstream response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/invalid_upstream.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(exceptions.InvalidUpstreamException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.tech.500"
    assert (
        excinfo.value.error_details
        == "Invalid response from the upstream server (The request sent to the GDC"
        " is erroneous) ; 502 Bad Gateway"
    )


def test_vehicle_error_not_supported() -> None:
    """Test vehicle not_supported response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/not_supported.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(exceptions.NotSupportedException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.tech.501"
    assert (
        excinfo.value.error_details
        == "This feature is not technically supported by this gateway"
    )


def test_vehicle_error_resource_not_found() -> None:
    """Test vehicle resource_not_found response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/resource_not_found.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(exceptions.ResourceNotFoundException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.wired.notFound"
    assert excinfo.value.error_details == "Resource not found"


def test_vehicle_error_access_denied() -> None:
    """Test vehicle access_denied response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/access_denied.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(exceptions.AccessDeniedException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.403"
    assert excinfo.value.error_details == "Access is denied for this resource"
