"""Test cases for the Renault client API keys."""

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses

from renault_api.const import AVAILABLE_LOCALES
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.const import LOCALE_BASE_URL
from renault_api.exceptions import RenaultException
from renault_api.helpers import get_api_keys


@pytest.mark.asyncio()
@pytest.mark.parametrize("locale", AVAILABLE_LOCALES.keys())
async def test_available_locales(locale: str) -> None:
    """Ensure all items AVAILABLE_LOCALES have correct data."""
    expected_api_keys = AVAILABLE_LOCALES[locale]

    api_keys = await get_api_keys(locale)
    assert api_keys == expected_api_keys
    for key in [
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        assert api_keys[key]


@pytest.mark.asyncio()
async def test_missing_aiohttp_session() -> None:
    """Ensure failure to unknown locale if aiohttp_session is not set."""
    locale = "invalid"

    with pytest.raises(RenaultException) as excinfo:
        await get_api_keys(locale)
    assert "aiohttp_session is not set." in str(excinfo)


@pytest.mark.asyncio()
@pytest.mark.parametrize("locale", AVAILABLE_LOCALES.keys())
@pytest.mark.skip(reason="Makes real calls to Renault servers")
async def test_preload_force_api_keys(websession: ClientSession, locale: str) -> None:
    """Ensure is able to parse a valid locale from Renault servers."""
    expected_api_keys = AVAILABLE_LOCALES[locale]

    api_keys = await get_api_keys(locale, True, websession)

    assert api_keys == expected_api_keys


@pytest.mark.asyncio()
@pytest.mark.skip("API keys are out of date.")
async def test_preload_unknown_api_keys(
    websession: ClientSession, mocked_responses: aioresponses
) -> None:
    """Ensure is able to parse a known known."""
    expected_api_keys = AVAILABLE_LOCALES["fr_FR"]

    fake_locale = "invalid"
    fake_url = f"{LOCALE_BASE_URL}/configuration/android/config_{fake_locale}.json"
    with open("tests/fixtures/config_sample.txt", "r") as f:
        fake_body = f.read()

    mocked_responses.get(fake_url, status=200, body=fake_body)

    api_keys = await get_api_keys(fake_locale, websession=websession)

    assert api_keys == expected_api_keys


@pytest.mark.asyncio()
async def test_preload_invalid_api_keys(
    websession: ClientSession, mocked_responses: aioresponses
) -> None:
    """Ensure is able to parse an invalid locale."""
    fake_locale = "fake"
    fake_url = f"{LOCALE_BASE_URL}/configuration/android/config_{fake_locale}.json"

    mocked_responses.get(fake_url, status=404)

    with pytest.raises(RenaultException) as excinfo:
        await get_api_keys(fake_locale, websession=websession)
    assert "Locale not found on Renault server" in str(excinfo)
