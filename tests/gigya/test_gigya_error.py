"""Tests for Gigya errors."""

import pytest

from tests import fixtures

from renault_api.gigya import exceptions
from renault_api.gigya import models
from renault_api.gigya import schemas
from renault_api.gigya.enums import GigyaErrorCode

WRONG_CODE_FIXTURE = (
    f"{fixtures.GIGYA_FIXTURE_PATH}/error/tfa_complete_email_verification.400006.json"
)


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


def test_tfa_complete_email_verification_400006_response() -> None:
    """Test completeVerification.400006 (wrong verification code) response."""
    response = fixtures.get_file_content_as_schema(
        WRONG_CODE_FIXTURE, schemas.GigyaTfaEmailCompleteVerificationResponseSchema
    )
    with pytest.raises(exceptions.InvalidVerificationCodeException) as excinfo:
        response.raise_for_error_code()
    assert excinfo.value.error_code == GigyaErrorCode.INVALID_VERIFICATION_CODE
    assert excinfo.value.error_details == "Wrong verification code"


def test_400006_from_other_endpoint() -> None:
    """Test 400006 from another endpoint is a generic error.

    400006 is Gigya's generic "invalid parameter value" code: it only means a
    wrong verification code when completing the email verification.
    """
    response: models.GigyaLoginResponse = fixtures.get_file_content_as_schema(
        WRONG_CODE_FIXTURE,
        schemas.GigyaLoginResponseSchema,
    )
    with pytest.raises(exceptions.GigyaResponseException) as excinfo:
        response.raise_for_error_code()
    assert type(excinfo.value) is exceptions.GigyaResponseException
    assert excinfo.value.error_code == 400006


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


@pytest.mark.parametrize(
    "exception",
    [
        exceptions.GigyaResponseException(400006, "Wrong verification code"),
        exceptions.GigyaResponseException(
            error_code=400006, error_details="Wrong verification code"
        ),
        exceptions.InvalidCredentialsException(400006, "Wrong verification code"),
    ],
)
def test_response_exception_output(
    exception: exceptions.GigyaResponseException,
) -> None:
    """Test the error code and details are shown, however it is created."""
    assert exception.args == (400006, "Wrong verification code")
    assert str(exception) == "(400006, 'Wrong verification code')"
    assert exception.error_code == 400006
    assert exception.error_details == "Wrong verification code"


def test_pending_two_factor_authentication_exception_output() -> None:
    """Test the reg token is kept out of the exception output."""
    exception = exceptions.PendingTwoFactorAuthenticationException(
        403101, "Pending Two-Factor Authentication", "sample-reg-token"
    )
    assert exception.args == (403101, "Pending Two-Factor Authentication")
    assert str(exception) == "(403101, 'Pending Two-Factor Authentication')"
    assert "sample-reg-token" not in repr(exception)
    assert exception.reg_token == "sample-reg-token"
