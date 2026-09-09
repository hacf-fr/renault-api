"""Tests for Gigya models."""

import pytest

from tests import fixtures

from renault_api.gigya import exceptions
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


def test_tfa_init_response() -> None:
    """Test initTFA response."""
    response: models.GigyaTfaInitResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/tfa_init.json",
        schemas.GigyaTfaInitResponseSchema,
    )
    response.raise_for_error_code()
    assert response.get_gigya_assertion() == "sample-gigya-assertion"


def test_tfa_init_response_missing_assertion() -> None:
    """Test initTFA response with no gigyaAssertion."""
    response = models.GigyaTfaInitResponse(
        raw_data={}, errorCode=0, errorDetails=None, regToken=None, gigyaAssertion=None
    )
    with pytest.raises(exceptions.GigyaException):
        response.get_gigya_assertion()


def test_tfa_emails_response() -> None:
    """Test TFA email list response."""
    response: models.GigyaTfaEmailListResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/tfa_emails.json",
        schemas.GigyaTfaEmailListResponseSchema,
    )
    response.raise_for_error_code()
    assert response.get_email_id() == "sample-email-id"


def test_tfa_emails_response_empty() -> None:
    """Test TFA email list response with no registered emails."""
    response = models.GigyaTfaEmailListResponse(
        raw_data={}, errorCode=0, errorDetails=None, regToken=None, emails=[]
    )
    with pytest.raises(exceptions.GigyaException):
        response.get_email_id()


def test_tfa_send_email_code_response() -> None:
    """Test sendVerificationCode response."""
    response: models.GigyaTfaSendEmailCodeResponse = (
        fixtures.get_file_content_as_schema(
            f"{fixtures.GIGYA_FIXTURE_PATH}/tfa_send_email_code.json",
            schemas.GigyaTfaSendEmailCodeResponseSchema,
        )
    )
    response.raise_for_error_code()
    assert response.get_phv_token() == "sample-phv-token"


def test_tfa_send_email_code_response_missing_token() -> None:
    """Test sendVerificationCode response with no phvToken."""
    response = models.GigyaTfaSendEmailCodeResponse(
        raw_data={}, errorCode=0, errorDetails=None, regToken=None, phvToken=None
    )
    with pytest.raises(exceptions.GigyaException):
        response.get_phv_token()


def test_tfa_complete_email_verification_response() -> None:
    """Test completeVerification response."""
    response = fixtures.get_file_content_as_schema(
        f"{fixtures.GIGYA_FIXTURE_PATH}/tfa_complete_email_verification.json",
        schemas.GigyaTfaEmailCompleteVerificationResponseSchema,
    )
    response.raise_for_error_code()
    assert response.get_provider_assertion() == "sample-provider-assertion"


def test_tfa_complete_email_verification_response_missing_assertion() -> None:
    """Test completeVerification response with no providerAssertion."""
    response = models.GigyaTfaEmailCompleteVerificationResponse(
        raw_data={},
        errorCode=0,
        errorDetails=None,
        regToken=None,
        providerAssertion=None,
    )
    with pytest.raises(exceptions.GigyaException):
        response.get_provider_assertion()
