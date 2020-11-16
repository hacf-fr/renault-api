"""Tests for RenaultClient."""
import pytest

from renault_api.exceptions import GigyaResponseException
from renault_api.model.gigya import GigyaGetAccountInfoResponse
from renault_api.model.gigya import GigyaGetAccountInfoResponseSchema
from renault_api.model.gigya import GigyaGetJWTResponse
from renault_api.model.gigya import GigyaGetJWTResponseSchema
from renault_api.model.gigya import GigyaLoginResponse
from renault_api.model.gigya import GigyaLoginResponseSchema


def test_login_response() -> None:
    """Test login response."""
    mock_login_response = {
        "errorCode": 0,
        "sessionInfo": {"cookieValue": "sample-cookie-value"},
    }
    response: GigyaLoginResponse = GigyaLoginResponseSchema.load(mock_login_response)
    response.raise_for_error_code()
    assert response.session_info.cookie_value == "sample-cookie-value"


def test_login_failed_response() -> None:
    """Test login response."""
    mock_login_response = {
        "errorCode": 403042,
        "errorDetails": "invalid loginID or password",
        "errorMessage": "Invalid LoginID",
    }
    response: GigyaLoginResponse = GigyaLoginResponseSchema.load(mock_login_response)
    with pytest.raises(GigyaResponseException) as excinfo:
        response.raise_for_error_code()
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


def test_get_account_info_response() -> None:
    """Test login response."""
    mock_get_account_info_response = {
        "errorCode": 0,
        "data": {"personId": "person-id-1"},
    }
    response: GigyaGetAccountInfoResponse = GigyaGetAccountInfoResponseSchema.load(
        mock_get_account_info_response
    )
    response.raise_for_error_code()
    assert response.data.person_id == "person-id-1"


def test_get_jwt_response() -> None:
    """Test login response."""
    mock_get_jwt_response = {
        "errorCode": 0,
        "id_token": "sample-jwt-token",
    }
    response: GigyaGetJWTResponse = GigyaGetJWTResponseSchema.load(
        mock_get_jwt_response
    )
    response.raise_for_error_code()
    assert response.id_token == "sample-jwt-token"
