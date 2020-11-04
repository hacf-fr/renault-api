"""Core functions for the CLI."""
import logging
import os
from datetime import datetime
from locale import getdefaultlocale
from typing import Optional

import click

from renault_api.const import CONF_LOCALE, PERMANENT_KEYS
from renault_api.credential_store import CredentialStore
from renault_api.credential_store import FileCredentialStore
from renault_api.exceptions import RenaultException
from renault_api.helpers import get_api_keys
from renault_api.model.credential import Credential

CONF_ACCOUNT_ID = "accound-id"
CONF_VIN = "vin"


class CLICredentialStore:
    """Singleton of the CredentialStore for the CLI."""

    __instance: CredentialStore = None

    def __new__(cls):
        """Get singleton Credential Store."""
        if not CLICredentialStore.__instance:
            CLICredentialStore.__instance = FileCredentialStore(
                os.path.expanduser("~/.credentials/renault-api.json")
            )
        return CLICredentialStore.__instance


def set_debug(debug: bool, log: bool) -> None:
    """Renault CLI."""
    if debug or log:
        renault_log = logging.getLogger("renault_api")
        renault_log.setLevel(logging.DEBUG)

        if log:
            # create formatter and add it to the handlers
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            # create file handler which logs even debug messages
            fh = logging.FileHandler(f"logs/{datetime.today():%Y-%m-%d}.log")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)

            # And enable our own debug logging
            renault_log.addHandler(fh)

        if debug:
            logging.basicConfig()

        renault_log.warning(
            "Debug output enabled. Logs may contain personally identifiable "
            "information and account credentials! Be sure to sanitise these logs "
            "before sending them to a third party or posting them online."
        )


async def set_options(
    websession, locale: Optional[str], account: Optional[str], vin: Optional[str]
) -> None:
    """Set configuration keys."""
    await set_options(locale, account, vin)
    if locale:
        await set_locale(websession, locale)
    if account:
        credential_store = CLICredentialStore()
        credential_store[CONF_ACCOUNT_ID] = Credential(account)
    if vin:
        credential_store = CLICredentialStore()
        credential_store[CONF_VIN] = Credential(vin)


async def ensure_locale(websession) -> None:
    """Prompt the user for locale."""
    credential_store = CLICredentialStore()
    if CONF_LOCALE in credential_store:
        return

    default_locale = getdefaultlocale()[0]
    while True:
        locale = click.prompt("Please select a locale", default=default_locale)
        try:
            await set_locale(websession, locale)
        except RenaultException as exc:
            click.echo(str(exc), err=True)
        else:
            return
        click.echo(f"Locale `{locale}` is unknown.", err=True)


async def set_locale(websession, locale: str) -> None:
    """Prompt the user for locale."""
    await get_api_keys(locale, aiohttp_session=websession)

    credential_store = CLICredentialStore()
    credential_store[CONF_LOCALE] = Credential(locale)


async def display_keys(websession) -> None:
    """Get the current configuration keys."""
    await ensure_locale(websession)
    credential_store = CLICredentialStore()
    for key in PERMANENT_KEYS:
        click.echo(f"Current {key}: {credential_store.get_value(key)}")
