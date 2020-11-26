"""Tests for Kamereon models."""
import pytest
from tests import get_json_files
from tests import get_response_content

from renault_api.exceptions import KamereonResponseException
from renault_api.model import kamereon as model


FIXTURE_PATH = "tests/fixtures/kamereon/error"


@pytest.mark.parametrize("filename", get_json_files(FIXTURE_PATH))
def test_vehicle_error_response(filename: str) -> None:
    """Test vehicle error response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        filename, model.KamereonVehicleDataResponseSchema
    )
    with pytest.raises(KamereonResponseException):
        response.raise_for_error_code()
    assert response.errors is not None


def test_vehicle_error_quota_limit() -> None:
    """Test vehicle quota_limit response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/quota_limit.json",
        model.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.wired.overloaded"
    assert excinfo.value.error_details == "You have reached your quota limit"


def test_vehicle_error_invalid_date() -> None:
    """Test vehicle invalid_date response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/invalid_date.json",
        model.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.400"
    assert (
        excinfo.value.error_details
        == "/data/attributes/startDateTime must be a future date"
    )


def test_vehicle_error_invalid_upstream() -> None:
    """Test vehicle invalid_upstream response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/invalid_upstream.json",
        model.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.tech.500"
    assert (
        excinfo.value.error_details
        == "Invalid response from the upstream server (The request sent to the GDC"
        " is erroneous) ; 502 Bad Gateway"
    )


def test_vehicle_error_not_supported() -> None:
    """Test vehicle not_supported response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/not_supported.json",
        model.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.tech.501"
    assert (
        excinfo.value.error_details
        == "This feature is not technically supported by this gateway"
    )


def test_vehicle_error_resource_not_found() -> None:
    """Test vehicle resource_not_found response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/resource_not_found.json",
        model.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.wired.notFound"
    assert excinfo.value.error_details == "Resource not found"


def test_vehicle_error_access_denied() -> None:
    """Test vehicle access_denied response."""
    response: model.KamereonVehicleDataResponse = get_response_content(
        f"{FIXTURE_PATH}/access_denied.json",
        model.KamereonVehicleDataResponseSchema,
    )
    with pytest.raises(KamereonResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == "err.func.403"
    assert excinfo.value.error_details == "Access is denied for this resource"
