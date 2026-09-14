"""Tests for Gigya errors."""

import pytest

from tests import fixtures

from renault_api.gigya import exceptions
from renault_api.gigya import models
from renault_api.gigya import schemas


@pytest.mark.parametrize(
    "filename", fixtures.get_json_files(f"{fixtures.GIGYA_FIXTURE_PATH}/error")
)
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
        f"{fixtures.GIGYA_FIXTURE_PATH}/error/get_jwt.403005.json",
        schemas.GigyaGetJWTResponseSchema,
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403005
    assert excinfo.value.error_details == "Unauthorized user"


def test_get_jwt_403013_response() -> None:
    """Test get_jwt.403013 response."""
    response: models.GigyaGetJWTResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/error/get_jwt.403013.json",
        schemas.GigyaGetJWTResponseSchema,
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403013
    assert excinfo.value.error_details == "Unverified user"


def test_login_403042_response() -> None:
    """Test login.403042 response."""
    response: models.GigyaLoginResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/error/login.403042.json",
        schemas.GigyaLoginResponseSchema,
    )
    with pytest.raises(exceptions.InvalidCredentialsException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403042
    assert excinfo.value.error_details == "invalid loginID or password"


def test_login_403101_response() -> None:
    """Test login.403101 (pending two-factor authentication) response."""
    response: models.GigyaLoginResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/error/login.403101.json",
        schemas.GigyaLoginResponseSchema,
    )
    with pytest.raises(exceptions.PendingTwoFactorAuthenticationException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == 403101
    assert excinfo.value.error_details == "Pending Two-Factor Authentication"
    assert excinfo.value.reg_token == "sample-reg-token"


def test_403101_without_reg_token() -> None:
    """A 403101 error without a regToken falls back to a generic error.

    This shouldn't happen in practice, but avoids raising
    `PendingTwoFactorAuthenticationException` with no usable `reg_token`.
    """
    response = models.GigyaResponse(
        raw_data={}, errorCode=403101, errorDetails="test", regToken=None
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert not isinstance(
        excinfo.value, exceptions.PendingTwoFactorAuthenticationException
    )
