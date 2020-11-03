"""Client for Renault API."""
import logging
from typing import Dict
from typing import Optional

import aiohttp
from aiohttp.client_exceptions import ClientResponseError

from .const import AVAILABLE_LOCALES
from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .exceptions import RenaultException

_LOGGER = logging.getLogger(__package__)


class RenaultClient:
    """Proxy to the Renault API."""

    def __init__(self) -> None:
        """Initialise Renault Client."""
        self.aiohttp_session: Optional[aiohttp.ClientSession] = None

    async def preload_api_keys(self, locale: str) -> Dict[str, str]:
        """Load the credential store with API Keys.

        Args:
            locale (str): locale code (preferrably from AVAILABLE_LOCALES.keys()).

        Returns:
            Dict with gigya-api-key, gigya-api-url,
            kamereon-api-key and kamereon-api-url

        Raises:
            RenaultException: an issue occured loading the API keys
        """
        if locale in AVAILABLE_LOCALES.keys():
            return AVAILABLE_LOCALES[locale]
        else:
            _LOGGER.warning(
                "Locale %s was not found in AVAILABLE_LOCALES. "
                "Attempting to load details from Renault servers.",
                locale,
            )
            if self.aiohttp_session is None:
                raise RenaultException("aiohttp_session is not set.")

            url = f"https://renault-wrd-prod-1-euw1-myrapp-one.s3-eu-west-1.amazonaws.com/configuration/android/config_{locale}.json"  # noqa
            async with self.aiohttp_session.get(url) as response:
                try:
                    response.raise_for_status()
                except ClientResponseError as exc:
                    raise RenaultException(
                        f"Locale not found on Renault server ({exc.status})."
                    ) from exc
                response_body = await response.json(content_type=None)

                _LOGGER.debug(
                    "Received api keys from myrenault response: %s", response_body
                )

                servers = response_body["servers"]
                return {
                    CONF_GIGYA_APIKEY: servers["gigyaProd"]["apikey"],
                    CONF_GIGYA_URL: servers["gigyaProd"]["target"],
                    CONF_KAMEREON_APIKEY: servers["wiredProd"]["apikey"],
                    CONF_KAMEREON_URL: servers["wiredProd"]["target"],
                }
