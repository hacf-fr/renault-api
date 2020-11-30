"""Tests for Gigya models."""
import pytest
from tests import get_json_files
from tests import get_response_content

from renault_api.gigya import models
from renault_api.gigya import schemas

FIXTURE_PATH = "tests/fixtures/gigya"


@pytest.mark.parametrize("filename", get_json_files(FIXTURE_PATH))
def test_valid_response(filename: str) -> None:
    """Test all valid responses."""
    response: models.GigyaResponse = get_response_content(
        filename, schemas.GigyaResponseSchema
    )
    response.raise_for_error_code()


def test_login_response() -> None:
    """Test login response."""
    response: models.GigyaLoginResponse = get_response_content(
        f"{FIXTURE_PATH}/login.json", schemas.GigyaLoginResponseSchema
    )
    response.raise_for_error_code()
    assert response.get_session_cookie() == "sample-cookie-value"


def test_get_account_info_response() -> None:
    """Test get_account_info response."""
    response: models.GigyaGetAccountInfoResponse = get_response_content(
        f"{FIXTURE_PATH}/get_account_info.json",
        schemas.GigyaGetAccountInfoResponseSchema,
    )
    response.raise_for_error_code()
    assert response.get_person_id() == "person-id-1"


def test_get_jwt_response() -> None:
    """Test get_jwt response."""
    response: models.GigyaGetJWTResponse = get_response_content(
        f"{FIXTURE_PATH}/get_jwt.json", schemas.GigyaGetJWTResponseSchema
    )
    response.raise_for_error_code()
    assert response.get_jwt() == "sample-jwt-token"
