"""Test cases for the Renault client API keys."""
from typing import AsyncGenerator

import pytest
from aiohttp import ClientSession
from aioresponses import aioresponses  # type: ignore

from renault_api.client import RenaultClient
from renault_api.const import AVAILABLE_LOCALES
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.const import LOCALE_BASE_URL
from renault_api.exceptions import RenaultException


@pytest.fixture
async def renault_client() -> AsyncGenerator[RenaultClient, None]:
    """Fixture for testing RenaultClient."""
    async with ClientSession() as aiohttp_session:
        client = RenaultClient()
        client.aiohttp_session = aiohttp_session

        yield client


@pytest.mark.asyncio
@pytest.mark.parametrize("locale", AVAILABLE_LOCALES.keys())
async def test_available_locales(locale: str) -> None:
    """Ensure all items AVAILABLE_LOCALES have correct data."""
    expected_api_keys = AVAILABLE_LOCALES[locale]

    renault_client = RenaultClient()
    api_keys = await renault_client.preload_api_keys(locale)
    assert api_keys == expected_api_keys
    for key in [
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        assert api_keys[key]


@pytest.mark.asyncio
async def test_missing_aiohttp_session() -> None:
    """Ensure is able to parse a known known."""
    locale = "invalid"

    renault_client = RenaultClient()
    with pytest.raises(RenaultException) as excinfo:
        await renault_client.preload_api_keys(locale)
    assert "aiohttp_session is not set." in str(excinfo)


@pytest.mark.asyncio
async def test_preload_unknown_api_keys(renault_client: RenaultClient) -> None:
    """Ensure is able to parse a known known."""
    expected_api_keys = AVAILABLE_LOCALES["fr_FR"]

    fake_locale = "invalid"
    fake_url = f"{LOCALE_BASE_URL}/configuration/android/config_{fake_locale}.json"
    with open("tests/fixtures/config_sample.txt", "r") as f:
        fake_body = f.read()

    with aioresponses() as mock_aioresponses:
        mock_aioresponses.get(fake_url, status=200, body=fake_body)

        api_keys = await renault_client.preload_api_keys(fake_locale)

        assert api_keys == expected_api_keys


@pytest.mark.asyncio
async def test_preload_invalid_api_keys(renault_client: RenaultClient) -> None:
    """Ensure is able to parse an invalid locale."""
    fake_locale = "fake"
    fake_url = f"https://renault-wrd-prod-1-euw1-myrapp-one.s3-eu-west-1.amazonaws.com/configuration/android/config_{fake_locale}.json"  # noqa

    with aioresponses() as mock_aioresponses:
        mock_aioresponses.get(fake_url, status=404)

        with pytest.raises(RenaultException) as excinfo:
            await renault_client.preload_api_keys(fake_locale)
        assert "Locale not found on Renault server" in str(excinfo)
