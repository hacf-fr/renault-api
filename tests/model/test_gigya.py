"""Tests for Gigya models."""
from tests import get_response_content

from renault_api.model import gigya as model

FIXTURE_PATH = "tests/fixtures/gigya"


def test_login_response() -> None:
    """Test login response."""
    response: model.GigyaLoginResponse = get_response_content(
        f"{FIXTURE_PATH}/login.json", model.GigyaLoginResponseSchema
    )
    assert response.get_session_cookie() == "sample-cookie-value"


def test_get_account_info_response() -> None:
    """Test login response."""
    response: model.GigyaGetAccountInfoResponse = get_response_content(
        f"{FIXTURE_PATH}/account_info.json", model.GigyaGetAccountInfoResponseSchema
    )
    response.raise_for_error_code()
    assert response.get_person_id() == "person-id-1"


def test_get_jwt_response() -> None:
    """Test login response."""
    response: model.GigyaGetJWTResponse = get_response_content(
        f"{FIXTURE_PATH}/get_jwt.json", model.GigyaGetJWTResponseSchema
    )
    response.raise_for_error_code()
    assert response.get_jwt() == "sample-jwt-token"
