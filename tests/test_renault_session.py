"""Test cases for initialisation of the Kamereon client."""

from typing import cast

import aiohttp
import pytest
from aiointercept import aiointercept
from yarl import URL

from tests import fixtures
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.test_credential_store import get_logged_in_credential_store

from renault_api.credential import JWTCredential
from renault_api.exceptions import NotAuthenticatedException
from renault_api.exceptions import RenaultException
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya.enums import GigyaErrorCode
from renault_api.gigya.exceptions import InvalidVerificationCodeException
from renault_api.gigya.exceptions import PendingTwoFactorAuthenticationException
from renault_api.renault_session import RenaultSession


def get_logged_in_session(websession: aiohttp.ClientSession) -> RenaultSession:
    """Get initialised RenaultSession."""
    return RenaultSession(
        websession=websession,
        country=TEST_COUNTRY,
        locale=TEST_LOCALE,
        locale_details=TEST_LOCALE_DETAILS,
        credential_store=get_logged_in_credential_store(),
    )


@pytest.fixture
def session(websession: aiohttp.ClientSession) -> RenaultSession:
    """Fixture for testing RenaultSession."""
    return RenaultSession(
        websession=websession,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
    )


@pytest.mark.asyncio
async def test_init_locale_only(websession: aiohttp.ClientSession) -> None:
    """Test initialisation with locale only."""
    session = RenaultSession(
        websession=websession,
        locale=TEST_LOCALE,
    )
    assert await session._get_country()
    assert await session._get_gigya_api_key()
    assert await session._get_gigya_root_url()
    assert await session._get_kamereon_api_key()
    assert await session._get_kamereon_root_url()


@pytest.mark.asyncio
async def test_init_country_only(websession: aiohttp.ClientSession) -> None:
    """Test initialisation with country only."""
    session = RenaultSession(
        websession=websession,
        country=TEST_COUNTRY,
    )
    assert await session._get_country()
    with pytest.raises(
        RenaultException,
        match="Credential `gigya-api-key` not found in credential cache.",
    ):
        assert await session._get_gigya_api_key()
    with pytest.raises(
        RenaultException,
        match="Credential `gigya-root-url` not found in credential cache.",
    ):
        assert await session._get_gigya_root_url()
    with pytest.raises(
        RenaultException,
        match="Credential `kamereon-api-key` not found in credential cache.",
    ):
        assert await session._get_kamereon_api_key()
    with pytest.raises(
        RenaultException,
        match="Credential `kamereon-root-url` not found in credential cache.",
    ):
        assert await session._get_kamereon_root_url()


@pytest.mark.asyncio
async def test_init_locale_details_only(websession: aiohttp.ClientSession) -> None:
    """Test initialisation with locale_details only."""
    session = RenaultSession(
        websession=websession,
        locale_details=TEST_LOCALE_DETAILS,
    )
    with pytest.raises(
        RenaultException,
        match="Credential `country` not found in credential cache.",
    ):
        assert await session._get_country()
    assert await session._get_gigya_api_key()
    assert await session._get_gigya_root_url()
    assert await session._get_kamereon_api_key()
    assert await session._get_kamereon_root_url()


@pytest.mark.asyncio
async def test_init_locale_and_details(websession: aiohttp.ClientSession) -> None:
    """Test initialisation with locale and locale_details."""
    session = RenaultSession(
        websession=websession,
        locale=TEST_LOCALE,
        locale_details=TEST_LOCALE_DETAILS,
    )
    assert await session._get_country()
    assert await session._get_gigya_api_key()
    assert await session._get_gigya_root_url()
    assert await session._get_kamereon_api_key()
    assert await session._get_kamereon_root_url()


@pytest.mark.asyncio
async def test_init_locale_country(websession: aiohttp.ClientSession) -> None:
    """Test initialisation with locale and country."""
    session = RenaultSession(
        websession=websession,
        locale=TEST_LOCALE,
        country=TEST_COUNTRY,
    )
    assert await session._get_country()
    assert await session._get_gigya_api_key()
    assert await session._get_gigya_root_url()
    assert await session._get_kamereon_api_key()
    assert await session._get_kamereon_root_url()


@pytest.mark.asyncio
async def test_not_logged_in(session: RenaultSession) -> None:
    """Test errors when not logged in."""
    with pytest.raises(
        NotAuthenticatedException,
        match="Gigya login token not available.",
    ):
        await session._get_login_token()

    with pytest.raises(
        NotAuthenticatedException,
        match="Gigya login token not available.",
    ):
        await session._get_person_id()

    with pytest.raises(
        NotAuthenticatedException,
        match="Gigya login token not available.",
    ):
        await session._get_jwt()


@pytest.mark.asyncio
async def test_login(session: RenaultSession, mocked_responses: aiointercept) -> None:
    """Test login/person/jwt response."""
    fixtures.inject_gigya_all(mocked_responses)

    await session.login(TEST_USERNAME, TEST_PASSWORD)
    assert await session._get_login_token() == TEST_LOGIN_TOKEN
    assert len(mocked_responses.requests) == 1

    assert await session._get_person_id() == TEST_PERSON_ID
    assert len(mocked_responses.requests) == 2

    assert await session._get_jwt()
    assert len(mocked_responses.requests) == 3

    # Ensure further requests use cache
    assert await session._get_person_id() == TEST_PERSON_ID
    assert await session._get_jwt()
    assert len(mocked_responses.requests) == 3


@pytest.mark.asyncio
async def test_login_two_factor_auth_required(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test login raises PendingTwoFactorAuthenticationException."""
    fixtures.inject_gigya_login_403101(mocked_responses)

    with pytest.raises(PendingTwoFactorAuthenticationException) as excinfo:
        await session.login(TEST_USERNAME, TEST_PASSWORD)
    assert excinfo.value.error_code == GigyaErrorCode.PENDING_TWO_FACTOR_AUTHENTICATION
    assert excinfo.value.reg_token == "sample-reg-token"
    assert session.login_token is None
    assert len(mocked_responses.requests) == 1


TEST_DEVICE_IDS = {"gmid": "sample-gmid", "ucid": "sample-ucid"}


@pytest.mark.asyncio
async def test_two_factor_auth(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test the full two-factor authentication flow, with a single email."""
    fixtures.inject_gigya_tfa_all(mocked_responses)

    with pytest.raises(PendingTwoFactorAuthenticationException):
        await session.login(TEST_USERNAME, TEST_PASSWORD)
    await session.request_two_factor_auth_code()
    await session.complete_two_factor_auth("123456")

    assert session.login_token == TEST_LOGIN_TOKEN
    assert session.device_ids == TEST_DEVICE_IDS

    first_login, second_login = fixtures.get_gigya_requests(
        mocked_responses, "accounts.login"
    )
    assert not first_login.cookies
    assert dict(second_login.cookies) == TEST_DEVICE_IDS
    (send_code,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.email.sendVerificationCode"
    )
    assert send_code.query["emailID"] == "sample-email-id"
    assert "lang" not in send_code.query
    (finalize,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.finalizeTFA"
    )
    assert finalize.query["tempDevice"] == "false"

    # The challenge is resolved
    with pytest.raises(RenaultException, match="No two-factor authentication"):
        await session.complete_two_factor_auth("123456")


@pytest.mark.asyncio
async def test_two_factor_auth_wrong_code(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test a wrong code can be retried, without requesting a new code."""
    fixtures.inject_gigya_login_403101(mocked_responses)
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)
    fixtures.inject_gigya_tfa_emails(mocked_responses)
    fixtures.inject_gigya_tfa_send_email_code(mocked_responses)
    fixtures.inject_gigya_tfa_complete_email_verification(
        mocked_responses, "error/tfa_complete_email_verification.400006.json"
    )
    fixtures.inject_gigya_tfa_complete_email_verification(mocked_responses)
    fixtures.inject_gigya_tfa_finalize(mocked_responses)
    fixtures.inject_gigya_login(mocked_responses)

    with pytest.raises(PendingTwoFactorAuthenticationException):
        await session.login(TEST_USERNAME, TEST_PASSWORD)
    await session.request_two_factor_auth_code()

    with pytest.raises(InvalidVerificationCodeException):
        await session.complete_two_factor_auth("000000")
    assert session.login_token is None
    assert session._pending_tfa is not None

    await session.complete_two_factor_auth("123456")
    assert session.login_token == TEST_LOGIN_TOKEN
    assert session._pending_tfa is None

    first, second = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.email.completeVerification"
    )
    assert first.query["code"] == "000000"
    assert second.query["code"] == "123456"
    assert second.query["phvToken"] == first.query["phvToken"]
    assert (
        len(
            fixtures.get_gigya_requests(
                mocked_responses, "accounts.tfa.email.sendVerificationCode"
            )
        )
        == 1
    )


@pytest.mark.asyncio
async def test_two_factor_auth_multiple_emails(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test two-factor authentication with several emails, and a locale."""
    session = RenaultSession(
        websession=websession,
        locale=TEST_LOCALE,
        country=TEST_COUNTRY,
        locale_details=TEST_LOCALE_DETAILS,
    )
    fixtures.inject_gigya_login_403101(mocked_responses)
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)
    fixtures.inject_gigya_tfa_emails(mocked_responses, "tfa_get_emails.multiple.json")
    fixtures.inject_gigya_tfa_emails(mocked_responses, "tfa_get_emails.multiple.json")
    fixtures.inject_gigya_tfa_send_email_code(mocked_responses)

    with pytest.raises(PendingTwoFactorAuthenticationException):
        await session.login(TEST_USERNAME, TEST_PASSWORD)

    emails = await session.get_two_factor_auth_emails()
    assert [(email.id, email.obfuscated) for email in emails] == [
        ("sample-email-id", "e***@example.com"),
        ("sample-email-id-2", "o***@example.com"),
    ]
    with pytest.raises(RenaultException, match="`email_id` is required"):
        await session.request_two_factor_auth_code()

    await session.request_two_factor_auth_code("sample-email-id-2")
    (send_code,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.email.sendVerificationCode"
    )
    assert send_code.query["emailID"] == "sample-email-id-2"
    assert send_code.query["lang"] == "fr"
    # The challenge is only started once
    assert (
        len(fixtures.get_gigya_requests(mocked_responses, "accounts.tfa.initTFA")) == 1
    )


@pytest.mark.asyncio
async def test_two_factor_auth_no_email(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test two-factor authentication without any registered email."""
    fixtures.inject_gigya_login_403101(mocked_responses)
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)
    fixtures.inject_gigya_tfa_emails(mocked_responses, "tfa_get_emails.empty.json")

    with pytest.raises(PendingTwoFactorAuthenticationException):
        await session.login(TEST_USERNAME, TEST_PASSWORD)
    with pytest.raises(RenaultException, match="No email address is registered"):
        await session.request_two_factor_auth_code()


@pytest.mark.asyncio
async def test_two_factor_auth_not_pending(session: RenaultSession) -> None:
    """Test two-factor authentication methods without a pending challenge."""
    with pytest.raises(RenaultException, match="call `login` first"):
        await session.get_two_factor_auth_emails()
    with pytest.raises(RenaultException, match="call `login` first"):
        await session.request_two_factor_auth_code("sample-email-id")
    with pytest.raises(RenaultException, match="call `login` first"):
        await session.complete_two_factor_auth("123456")


@pytest.mark.asyncio
async def test_complete_two_factor_auth_without_code(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test completing two-factor authentication before requesting a code."""
    fixtures.inject_gigya_login_403101(mocked_responses)

    with pytest.raises(PendingTwoFactorAuthenticationException):
        await session.login(TEST_USERNAME, TEST_PASSWORD)
    with pytest.raises(RenaultException, match="call `request_two_factor_auth_code`"):
        await session.complete_two_factor_auth("123456")


@pytest.mark.asyncio
async def test_device_ids(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test restored device ids are sent on login, whatever the cookie jar holds."""
    assert session.device_ids == {}
    session.set_device_ids(TEST_DEVICE_IDS)
    assert session.device_ids == TEST_DEVICE_IDS

    # Another user of the same aiohttp session
    session._websession.cookie_jar.update_cookies(
        {"gmid": "other-gmid", "ucid": "other-ucid"}, URL(TEST_GIGYA_URL)
    )
    fixtures.inject_gigya_login(mocked_responses)
    await session.login(TEST_USERNAME, TEST_PASSWORD)
    (request,) = fixtures.get_gigya_requests(mocked_responses, "accounts.login")
    assert dict(request.cookies) == TEST_DEVICE_IDS
    # Login doesn't forget the device
    assert session.device_ids == TEST_DEVICE_IDS

    session.set_device_ids({})
    assert session.device_ids == {}


@pytest.mark.asyncio
async def test_two_factor_auth_with_device_ids(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test two-factor authentication reuses known device ids."""
    session.set_device_ids(TEST_DEVICE_IDS)
    fixtures.inject_gigya_login_403101(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)
    fixtures.inject_gigya_tfa_emails(mocked_responses)

    with pytest.raises(PendingTwoFactorAuthenticationException):
        await session.login(TEST_USERNAME, TEST_PASSWORD)
    await session.get_two_factor_auth_emails()

    assert not fixtures.get_gigya_requests(mocked_responses, "accounts.webSdkBootstrap")
    (init,) = fixtures.get_gigya_requests(mocked_responses, "accounts.tfa.initTFA")
    assert dict(init.cookies) == TEST_DEVICE_IDS


@pytest.mark.asyncio
async def test_login_token_property(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test that the login token is exposed after login."""
    assert session.login_token is None

    fixtures.inject_gigya_all(mocked_responses)
    await session.login(TEST_USERNAME, TEST_PASSWORD)

    assert session.login_token == TEST_LOGIN_TOKEN


@pytest.mark.asyncio
async def test_set_login_token(
    session: RenaultSession, mocked_responses: aiointercept
) -> None:
    """Test restoring a login token instead of using the password."""
    session.set_login_token(TEST_LOGIN_TOKEN)

    assert session.login_token == TEST_LOGIN_TOKEN
    assert await session._get_login_token() == TEST_LOGIN_TOKEN

    # A restored token can mint a JWT without ever calling login.
    fixtures.inject_gigya_jwt(mocked_responses)
    assert await session._get_jwt()
    assert len(mocked_responses.requests) == 1


@pytest.mark.asyncio
async def test_expired_login_token(
    websession: aiohttp.ClientSession, mocked_responses: aiointercept
) -> None:
    """Test _get_jwt response on expired login token."""
    session = get_logged_in_session(websession=websession)
    fixtures.inject_gigya(
        mocked_responses,
        urlpath="accounts.getJWT",
        filename="error/get_jwt.403005.json",
    )

    # First attempt uses cached values
    assert await session._get_jwt()
    assert len(mocked_responses.requests) == 0

    assert GIGYA_JWT in session._credentials
    assert GIGYA_LOGIN_TOKEN in session._credentials

    # mark JWT as expired
    jwt_credential = cast(JWTCredential, session._credentials.get(GIGYA_JWT))
    jwt_credential.expiry = 1

    # first attempt show authentication as expired
    with pytest.raises(
        NotAuthenticatedException,
        match="Authentication expired.",
    ):
        assert await session._get_jwt()

    assert len(mocked_responses.requests) == 1
    assert GIGYA_JWT not in session._credentials
    assert GIGYA_LOGIN_TOKEN not in session._credentials

    # subsequent attempts just show not authenticated
    with pytest.raises(
        NotAuthenticatedException,
        match="Gigya login token not available.",
    ):
        assert await session._get_jwt()

    assert len(mocked_responses.requests) == 1
