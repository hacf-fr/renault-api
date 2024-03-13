"""Tests for Gigya models."""

import pytest

from tests import fixtures

from renault_api.gigya import models
from renault_api.gigya import schemas


@pytest.mark.parametrize(
    "filename", fixtures.get_json_files(fixtures.GIGYA_FIXTURE_PATH)
)
def test_valid_response(filename: str) -> None:
    """Test all valid responses."""
    response: models.GigyaResponse = fixtures.get_file_content_as_schema(
        filename, schemas.GigyaResponseSchema
    )
    response.raise_for_error_code()


def test_login_response() -> None:
    """Test login response."""
    response: models.GigyaLoginResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/login.json", schemas.GigyaLoginResponseSchema
    )
    response.raise_for_error_code()
    assert response.get_session_cookie() == "sample-cookie-value"


def test_get_account_info_response() -> None:
    """Test get_account_info response."""
    response: models.GigyaGetAccountInfoResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/get_account_info.json",
        schemas.GigyaGetAccountInfoResponseSchema,
    )
    response.raise_for_error_code()
    assert response.get_person_id() == "person-id-1"


def test_get_jwt_response() -> None:
    """Test get_jwt response."""
    response: models.GigyaGetJWTResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/get_jwt.json", schemas.GigyaGetJWTResponseSchema
    )
    response.raise_for_error_code()
    assert response.get_jwt() == "sample-jwt-token"
