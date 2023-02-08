"""Tests for Gigya API."""
from tests import fixtures
from tests.const import TEST_GIGYA_APIKEY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

import aiohttp
import pytest
from aioresponses import aioresponses

from renault_api import gigya


@pytest.mark.asyncio
async def test_login(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
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
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
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
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
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
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
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
