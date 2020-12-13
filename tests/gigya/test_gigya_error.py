"""Tests for Gigya errors."""
import pytest
from tests import fixtures

from renault_api.gigya import exceptions
from renault_api.gigya import models
from renault_api.gigya import schemas


FIXTURE_PATH = f"{fixtures.GIGYA_FIXTURE_PATH}/errors"


@pytest.mark.parametrize("filename", fixtures.get_json_files(FIXTURE_PATH))
def test_error_response(filename: str) -> None:
    """Test all error responses."""
    response: models.GigyaResponse = fixtures.get_file_content_as_schema(
        filename, schemas.GigyaResponseSchema
    )
    with pytest.raises(exceptions.GigyaResponseException):
        response.raise_for_error_code()


def test_get_jwt_403005_response() -> None:
    """Test get_jwt.403005 response."""
    response: models.GigyaGetJWTResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/get_jwt.403005.json", schemas.GigyaGetJWTResponseSchema
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403005
    assert excinfo.value.error_details == "Unauthorized user"


def test_get_jwt_403013_response() -> None:
    """Test get_jwt.403013 response."""
    response: models.GigyaGetJWTResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/get_jwt.403013.json", schemas.GigyaGetJWTResponseSchema
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403013
    assert excinfo.value.error_details == "Unverified user"


def test_login_403042_response() -> None:
    """Test login.403042 response."""
    response: models.GigyaLoginResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/login.403042.json", schemas.GigyaLoginResponseSchema
    )
    with pytest.raises(exceptions.InvalidCredentialsException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403042
    assert excinfo.value.error_details == "invalid loginID or password"
