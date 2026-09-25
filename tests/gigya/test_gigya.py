"""Tests for Gigya API."""

import aiohttp
import pytest
from aiointercept import aiointercept

from tests import fixtures
from tests.const import TEST_GIGYA_APIKEY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api import gigya


@pytest.mark.asyncio
async def test_login(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test login response."""
    fixtures.inject_gigya_login(mocked_responses)

    response = await gigya.login(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        TEST_USERNAME,
        TEST_PASSWORD,
    )
    assert response.get_session_cookie() == TEST_LOGIN_TOKEN


@pytest.mark.asyncio
async def test_login_error(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test login response."""
    fixtures.inject_gigya_login_invalid(mocked_responses)

    with pytest.raises(gigya.exceptions.GigyaException):
        await gigya.login(
            websession,
            TEST_GIGYA_URL,
            TEST_GIGYA_APIKEY,
            TEST_USERNAME,
            TEST_PASSWORD,
        )


@pytest.mark.asyncio
async def test_person_id(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test get_account_info response."""
    fixtures.inject_gigya_account_info(mocked_responses)

    response = await gigya.get_account_info(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        TEST_LOGIN_TOKEN,
    )
    assert response.get_person_id() == TEST_PERSON_ID


@pytest.mark.asyncio
async def test_get_jwt_token(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test get_jwt response."""
    fixtures.inject_gigya_jwt(mocked_responses)

    response = await gigya.get_jwt(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        TEST_LOGIN_TOKEN,
    )
    assert response.get_jwt()


@pytest.mark.asyncio
async def test_init_tfa(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test initTFA response."""
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)

    response = await gigya.init_tfa(
        websession, TEST_GIGYA_URL, TEST_GIGYA_APIKEY, "sample-reg-token"
    )
    assert response.get_gigya_assertion() == "sample-gigya-assertion"


@pytest.mark.asyncio
async def test_init_tfa_without_bootstrap_cookies(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test initTFA still works if webSdkBootstrap sets no cookies."""
    fixtures.inject_gigya_tfa_bootstrap_no_cookies(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)

    response = await gigya.init_tfa(
        websession, TEST_GIGYA_URL, TEST_GIGYA_APIKEY, "sample-reg-token"
    )
    assert response.get_gigya_assertion() == "sample-gigya-assertion"


@pytest.mark.asyncio
async def test_get_tfa_emails(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test TFA email list response."""
    fixtures.inject_gigya_tfa_emails(mocked_responses)

    response = await gigya.get_tfa_emails(
        websession, TEST_GIGYA_URL, TEST_GIGYA_APIKEY, "sample-gigya-assertion"
    )
    assert response.get_email_id() == "sample-email-id"


@pytest.mark.asyncio
async def test_send_tfa_email_code(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test sendVerificationCode response."""
    fixtures.inject_gigya_tfa_send_email_code(mocked_responses)

    response = await gigya.send_tfa_email_code(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        "sample-gigya-assertion",
        "sample-email-id",
    )
    assert response.get_phv_token() == "sample-phv-token"


@pytest.mark.asyncio
async def test_complete_tfa_email_verification(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test completeVerification response."""
    fixtures.inject_gigya_tfa_complete_email_verification(mocked_responses)

    response = await gigya.complete_tfa_email_verification(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        "sample-gigya-assertion",
        "sample-phv-token",
        "123456",
    )
    assert response.get_provider_assertion() == "sample-provider-assertion"


@pytest.mark.asyncio
async def test_finalize_tfa(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test finalizeTFA response."""
    fixtures.inject_gigya_tfa_finalize(mocked_responses)

    await gigya.finalize_tfa(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        "sample-gigya-assertion",
        "sample-provider-assertion",
        "sample-reg-token",
        remember_device=False,
    )
