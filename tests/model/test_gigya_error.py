"""Tests for Gigya models."""
import pytest
from tests import get_json_files
from tests import get_response_content

from renault_api.exceptions import GigyaResponseException
from renault_api.model import gigya as model


FIXTURE_PATH = "tests/fixtures/gigya/errors"


@pytest.mark.parametrize("filename", get_json_files(FIXTURE_PATH))
def test_vehicle_error_response(filename: str) -> None:
    """Test vehicle error response."""
    response: model.GigyaResponse = get_response_content(
        filename, model.GigyaResponseSchema
    )
    with pytest.raises(GigyaResponseException):
        response.raise_for_error_code()


def test_get_jwt_403005_response() -> None:
    """Test get_jwt.403005 response."""
    response: model.GigyaGetJWTResponse = get_response_content(
        f"{FIXTURE_PATH}/403005.json", model.GigyaGetJWTResponseSchema
    )
    with pytest.raises(GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403005
    assert excinfo.value.error_details == "Unauthorized user"


def test_get_jwt_403013_response() -> None:
    """Test get_jwt.403013 response."""
    response: model.GigyaGetJWTResponse = get_response_content(
        f"{FIXTURE_PATH}/403013.json", model.GigyaGetJWTResponseSchema
    )
    with pytest.raises(GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403013
    assert excinfo.value.error_details == "Unverified user"


def test_login_403042_response() -> None:
    """Test login.403042 response."""
    response: model.GigyaLoginResponse = get_response_content(
        f"{FIXTURE_PATH}/403042.json", model.GigyaLoginResponseSchema
    )
    with pytest.raises(GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403042
    assert excinfo.value.error_details == "invalid loginID or password"
