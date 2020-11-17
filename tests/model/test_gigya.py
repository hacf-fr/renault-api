"""Tests for RenaultClient."""
from typing import Any
from typing import Type

import pytest
from marshmallow.schema import Schema

from renault_api.exceptions import GigyaResponseException
from renault_api.model.gigya import GigyaGetAccountInfoResponse
from renault_api.model.gigya import GigyaGetAccountInfoResponseSchema
from renault_api.model.gigya import GigyaGetJWTResponse
from renault_api.model.gigya import GigyaGetJWTResponseSchema
from renault_api.model.gigya import GigyaLoginResponse
from renault_api.model.gigya import GigyaLoginResponseSchema


def get_response_content(path: str, schema: Type[Schema]) -> Any:
    """Read fixture text file as string."""
    with open(f"tests/fixtures/gigya/{path}", "r") as file:
        content = file.read()
    return schema.loads(content)


def test_login_response() -> None:
    """Test login response."""
    response: GigyaLoginResponse = get_response_content(
        "login.json", GigyaLoginResponseSchema
    )
    assert response.sessionInfo.cookieValue == "sample-cookie-value"


def test_login_failed_response() -> None:
    """Test login response."""
    response: GigyaLoginResponse = get_response_content(
        "login_failed.json", GigyaLoginResponseSchema
    )
    with pytest.raises(GigyaResponseException) as excinfo:
        response.raise_for_error_code()
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


def test_get_account_info_response() -> None:
    """Test login response."""
    response: GigyaGetAccountInfoResponse = get_response_content(
        "account_info.json", GigyaGetAccountInfoResponseSchema
    )
    response.raise_for_error_code()
    assert response.data.personId == "person-id-1"


def test_get_jwt_response() -> None:
    """Test login response."""
    response: GigyaGetJWTResponse = get_response_content(
        "get_jwt.json", GigyaGetJWTResponseSchema
    )
    response.raise_for_error_code()
    assert response.id_token == "sample-jwt-token"
