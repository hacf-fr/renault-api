"""Test cases for initialisation of the Kamereon client."""
from typing import cast

import aiohttp
import pytest
from aioresponses import aioresponses

from tests import fixtures
from tests.const import TEST_COUNTRY
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
async def test_login(session: RenaultSession, mocked_responses: aioresponses) -> None:
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
async def test_expired_login_token(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
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
