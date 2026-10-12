"""Tests for Gigya API."""

import aiohttp
import pytest
from aiointercept import aiointercept
from yarl import URL

from tests import fixtures
from tests.const import TEST_GIGYA_APIKEY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api import gigya

TEST_DEVICE_IDS = {"gmid": "sample-gmid", "ucid": "sample-ucid"}


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
        login_id=TEST_USERNAME,
        password=TEST_PASSWORD,
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
            login_id=TEST_USERNAME,
            password=TEST_PASSWORD,
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
async def test_login_with_device_ids(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test login sends the device ids as cookies."""
    fixtures.inject_gigya_login(mocked_responses)

    response = await gigya.login(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        login_id=TEST_USERNAME,
        password=TEST_PASSWORD,
        device_ids=TEST_DEVICE_IDS,
    )
    assert response.get_session_cookie() == TEST_LOGIN_TOKEN
    (request,) = fixtures.get_gigya_requests(mocked_responses, "accounts.login")
    assert dict(request.cookies) == TEST_DEVICE_IDS


@pytest.mark.asyncio
async def test_get_device_ids(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test webSdkBootstrap response."""
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)

    device_ids = await gigya.get_device_ids(
        websession, TEST_GIGYA_URL, TEST_GIGYA_APIKEY
    )
    assert device_ids == {"gmid": "sample-gmid", "ucid": "sample-ucid"}


@pytest.mark.asyncio
async def test_get_device_ids_ignores_cookie_jar(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test webSdkBootstrap only returns the cookies set by the response."""
    websession.cookie_jar.update_cookies({"gmid": "other-gmid"}, URL(TEST_GIGYA_URL))
    fixtures.inject_gigya_tfa_bootstrap_no_cookies(mocked_responses)

    device_ids = await gigya.get_device_ids(
        websession, TEST_GIGYA_URL, TEST_GIGYA_APIKEY
    )
    assert device_ids == {}


@pytest.mark.asyncio
async def test_init_tfa(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test initTFA response."""
    fixtures.inject_gigya_tfa_init(mocked_responses)

    response = await gigya.init_tfa(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        device_ids=TEST_DEVICE_IDS,
        reg_token="sample-reg-token",
    )
    assert response.get_gigya_assertion() == "sample-gigya-assertion"
    (request,) = fixtures.get_gigya_requests(mocked_responses, "accounts.tfa.initTFA")
    assert request.query["gmid"] == "sample-gmid"
    assert request.query["ucid"] == "sample-ucid"
    assert dict(request.cookies) == TEST_DEVICE_IDS


@pytest.mark.asyncio
async def test_get_tfa_emails(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test TFA email list response."""
    fixtures.inject_gigya_tfa_emails(mocked_responses)

    response = await gigya.get_tfa_emails(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        device_ids=TEST_DEVICE_IDS,
        gigya_assertion="sample-gigya-assertion",
    )
    assert response.get_email_id() == "sample-email-id"
    (request,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.email.getEmails"
    )
    assert dict(request.cookies) == TEST_DEVICE_IDS


@pytest.mark.asyncio
@pytest.mark.parametrize("lang", [None, "fr"])
async def test_send_tfa_email_code(
    websession: aiohttp.ClientSession,
    mocked_responses: aiointercept,
    lang: str | None,
) -> None:
    """Test sendVerificationCode response."""
    fixtures.inject_gigya_tfa_send_email_code(mocked_responses)

    response = await gigya.send_tfa_email_code(
        websession,
        TEST_GIGYA_URL,
        TEST_GIGYA_APIKEY,
        device_ids=TEST_DEVICE_IDS,
        gigya_assertion="sample-gigya-assertion",
        email_id="sample-email-id",
        lang=lang,
    )
    assert response.get_phv_token() == "sample-phv-token"
    (request,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.email.sendVerificationCode"
    )
    assert request.query.get("lang") == lang
    assert dict(request.cookies) == TEST_DEVICE_IDS


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
        device_ids=TEST_DEVICE_IDS,
        gigya_assertion="sample-gigya-assertion",
        phv_token="sample-phv-token",
        code="123456",
    )
    assert response.get_provider_assertion() == "sample-provider-assertion"
    (request,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.email.completeVerification"
    )
    assert dict(request.cookies) == TEST_DEVICE_IDS


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
        device_ids=TEST_DEVICE_IDS,
        gigya_assertion="sample-gigya-assertion",
        provider_assertion="sample-provider-assertion",
        reg_token="sample-reg-token",
        remember_device=False,
    )
    (request,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.finalizeTFA"
    )
    assert request.query["tempDevice"] == "true"
    assert dict(request.cookies) == TEST_DEVICE_IDS
