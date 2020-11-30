"""Tests for Gigya models."""
import pytest
from tests import get_json_files
from tests import get_response_content

from renault_api.gigya import exceptions
from renault_api.gigya import models
from renault_api.gigya import schemas


FIXTURE_PATH = "tests/fixtures/gigya/errors"


@pytest.mark.parametrize("filename", get_json_files(FIXTURE_PATH))
def test_vehicle_error_response(filename: str) -> None:
    """Test vehicle error response."""
    response: models.GigyaResponse = get_response_content(
        filename, schemas.GigyaResponseSchema
    )
    with pytest.raises(exceptions.GigyaResponseException):
        response.raise_for_error_code()


def test_get_jwt_403005_response() -> None:
    """Test get_jwt.403005 response."""
    response: models.GigyaGetJWTResponse = get_response_content(
        f"{FIXTURE_PATH}/get_jwt.403005.json", schemas.GigyaGetJWTResponseSchema
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403005
    assert excinfo.value.error_details == "Unauthorized user"


def test_get_jwt_403013_response() -> None:
    """Test get_jwt.403013 response."""
    response: models.GigyaGetJWTResponse = get_response_content(
        f"{FIXTURE_PATH}/get_jwt.403013.json", schemas.GigyaGetJWTResponseSchema
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403013
    assert excinfo.value.error_details == "Unverified user"


def test_login_403042_response() -> None:
    """Test login.403042 response."""
    response: models.GigyaLoginResponse = get_response_content(
        f"{FIXTURE_PATH}/login.403042.json", schemas.GigyaLoginResponseSchema
    )
    with pytest.raises(exceptions.InvalidCredentialsException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403042
    assert excinfo.value.error_details == "invalid loginID or password"
