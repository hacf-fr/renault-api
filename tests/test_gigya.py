"""Test cases for the Renault client API keys."""
import json
from typing import AsyncGenerator

import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses  # type: ignore
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.fixtures import gigya_responses

from renault_api.const import AVAILABLE_LOCALES
from renault_api.gigya import Gigya
from renault_api.helpers import create_aiohttp_closed_event


@pytest.fixture
async def websession() -> AsyncGenerator[ClientSession, None]:
    """Fixture for generating ClientSession."""
    async with ClientSession() as aiohttp_session:
        yield aiohttp_session

        closed_event = create_aiohttp_closed_event(aiohttp_session)
        await aiohttp_session.close()
        await closed_event.wait()


@pytest.mark.asyncio
async def test_gigya_client(websession: ClientSession) -> None:
    """Build RenaultClient for testing."""
    locale_details = AVAILABLE_LOCALES[TEST_LOCALE]
    gigya = Gigya(websession=websession, locale_details=locale_details)

    with aioresponses() as mocked_responses:
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.login",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert len(mocked_responses.requests) == 1


@pytest.mark.asyncio
async def test_gigya_person_id(websession: ClientSession) -> None:
    """Build RenaultClient for testing."""
    locale_details = AVAILABLE_LOCALES[TEST_LOCALE]
    gigya = Gigya(websession=websession, locale_details=locale_details)

    with aioresponses() as mocked_responses:
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.login",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETACCOUNTINFO),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert TEST_PERSON_ID == await gigya.get_person_id()
        assert len(mocked_responses.requests) == 2

        # Ensure request count doesn't go up and cached value is used
        assert TEST_PERSON_ID == await gigya.get_person_id()
        assert len(mocked_responses.requests) == 2


@pytest.mark.asyncio
async def test_gigya_jwt(websession: ClientSession) -> None:
    """Build RenaultClient for testing."""
    locale_details = AVAILABLE_LOCALES[TEST_LOCALE]
    gigya = Gigya(websession=websession, locale_details=locale_details)

    with aioresponses() as mocked_responses:
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.login",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_LOGIN),
            headers={"content-type": "text/javascript"},
        )
        mocked_responses.add(
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            "POST",
            status=200,
            body=json.dumps(gigya_responses.MOCK_GETJWT),
            headers={"content-type": "text/javascript"},
        )

        await gigya.login(TEST_USERNAME, TEST_PASSWORD)
        assert await gigya.get_jwt()
        assert len(mocked_responses.requests) == 2

        # Ensure request count doesn't go up and cached value is used
        assert await gigya.get_jwt()
        assert len(mocked_responses.requests) == 2
