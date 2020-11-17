"""Tests for RenaultClient."""
import ast
from typing import Any
from typing import Type
from marshmallow.schema import Schema

import pytest

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
        dict_value = ast.literal_eval(file.read())
    return schema.load(dict_value)


def test_login_response() -> None:
    """Test login response."""
    response: GigyaLoginResponse = get_response_content(
        "login.txt", GigyaLoginResponseSchema
    )
    assert response.sessionInfo.cookieValue == "sample-cookie-value"


def test_login_failed_response() -> None:
    """Test login response."""
    response: GigyaLoginResponse = get_response_content(
        "login_failed.txt", GigyaLoginResponseSchema
    )
    with pytest.raises(GigyaResponseException) as excinfo:
        response.raise_for_error_code()
        assert excinfo.value.error_code == 403042
        assert excinfo.value.error_details == "invalid loginID or password"


def test_get_account_info_response() -> None:
    """Test login response."""
    response: GigyaGetAccountInfoResponse = get_response_content(
        "account_info.txt", GigyaGetAccountInfoResponseSchema
    )
    response.raise_for_error_code()
    assert response.data.personId == "person-id-1"


def test_get_account_info_corrupted_response() -> None:
    """Test login response."""
    response: GigyaGetAccountInfoResponse = get_response_content(
        "account_info_corrupted.txt", GigyaGetAccountInfoResponseSchema
    )
    response.raise_for_error_code()
    assert response.data is None


def test_get_jwt_response() -> None:
    """Test login response."""
    response: GigyaGetJWTResponse = get_response_content(
        "get_jwt.txt", GigyaGetJWTResponseSchema
    )
    response.raise_for_error_code()
    assert response.id_token == "sample-jwt-token"


def test_get_jwt_corrupted_response() -> None:
    """Test login response."""
    response: GigyaGetJWTResponse = get_response_content(
        "get_jwt_corrupted.txt", GigyaGetJWTResponseSchema
    )
    response.raise_for_error_code()
    assert response.id_token is None
