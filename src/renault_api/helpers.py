"""Helpers for Renault API."""
import asyncio
import functools
import logging
from typing import Dict
from typing import Optional

import aiohttp

from .const import AVAILABLE_LOCALES
from .const import CONF_GIGYA_APIKEY
from .const import CONF_GIGYA_URL
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .const import LOCALE_BASE_URL
from .exceptions import RenaultException

_LOGGER = logging.getLogger(__package__)


async def get_api_keys(
    locale: str,
    force_load: bool = False,
    websession: Optional[aiohttp.ClientSession] = None,
) -> Dict[str, str]:
    """Get the API keys for specified locale.

    Args:
        locale (str): locale code (preferrably from AVAILABLE_LOCALES.keys())
        force_load (bool): bypass internal AVAILABLE_LOCALES
        websession (aiohttp.ClientSession): required if locale not in AVAILABLE_LOCALES

    Returns:
        Dict with gigya-api-key, gigya-api-url,
        kamereon-api-key and kamereon-api-url

    Raises:
        RenaultException: an issue occured loading the API keys
    """
    if locale in AVAILABLE_LOCALES.keys() and not force_load:
        return AVAILABLE_LOCALES[locale]
    else:
        _LOGGER.warning(
            "Locale %s was not found in AVAILABLE_LOCALES "
            "(or force_load used). "
            "Attempting to load details from Renault servers.",
            locale,
        )
        if websession is None:
            raise RenaultException("aiohttp_session is not set.")

        url = f"{LOCALE_BASE_URL}/configuration/android/config_{locale}.json"
        async with websession.get(url) as response:  # pragma: no cover
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as exc:
                raise RenaultException(
                    f"Locale not found on Renault server (HTTPStatus = {exc.status})."
                ) from exc
            # Server sometimes returns invalid content-type
            # eg. application/octet-stream
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


def create_aiohttp_closed_event(
    websession: aiohttp.ClientSession,
) -> asyncio.Event:  # pragma: no cover
    """Work around aiohttp issue that doesn't properly close transports on exit.

    See https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-639080209

    Args:
        websession (aiohttp.ClientSession): session for which to generate the event.

    Returns:
        An event that will be set once all transports have been properly closed.
    """
    transports = 0
    all_is_lost = asyncio.Event()

    def connection_lost(exc, orig_lost):  # type: ignore
        nonlocal transports

        try:
            orig_lost(exc)
        finally:
            transports -= 1
            if transports == 0:
                all_is_lost.set()

    def eof_received(orig_eof_received):  # type: ignore
        try:
            orig_eof_received()
        except AttributeError:
            # It may happen that eof_received() is called after
            # _app_protocol and _transport are set to None.
            pass

    for conn in websession.connector._conns.values():  # type: ignore
        for handler, _ in conn:
            proto = getattr(handler.transport, "_ssl_protocol", None)
            if proto is None:
                continue

            transports += 1
            orig_lost = proto.connection_lost
            orig_eof_received = proto.eof_received

            proto.connection_lost = functools.partial(
                connection_lost, orig_lost=orig_lost
            )
            proto.eof_received = functools.partial(
                eof_received, orig_eof_received=orig_eof_received
            )

    if transports == 0:
        all_is_lost.set()

    return all_is_lost
