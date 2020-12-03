"""Singletons for the CLI."""
import os
from locale import getdefaultlocale
from typing import Optional

import aiohttp
import click

from renault_api.const import CONF_LOCALE
from renault_api.const import PERMANENT_KEYS
from renault_api.credential import Credential
from renault_api.credential_store import CredentialStore
from renault_api.credential_store import FileCredentialStore
from renault_api.exceptions import RenaultException
from renault_api.helpers import get_api_keys

CONF_ACCOUNT_ID = "accound-id"
CONF_VIN = "vin"

CREDENTIAL_PATH = os.path.expanduser("~/.credentials/renault-api.json")


class CLICredentialStore:
    """Singleton of the CredentialStore for the CLI."""

    __instance: Optional[CredentialStore] = None

    @classmethod
    def get_instance(cls) -> CredentialStore:
        """Get singleton Credential Store."""
        if not CLICredentialStore.__instance:
            CLICredentialStore.__instance = FileCredentialStore(CREDENTIAL_PATH)
        return CLICredentialStore.__instance


async def set_options(
    websession: aiohttp.ClientSession,
    locale: Optional[str],
    account: Optional[str],
    vin: Optional[str],
) -> None:
    """Set configuration keys."""
    if locale:
        # Ensure API keys are available
        api_keys = await get_api_keys(locale, websession=websession)

        credential_store = CLICredentialStore.get_instance()
        credential_store[CONF_LOCALE] = Credential(locale)
        for k, v in api_keys.items():
            credential_store[k] = Credential(v)

    if account:
        credential_store = CLICredentialStore.get_instance()
        credential_store[CONF_ACCOUNT_ID] = Credential(account)
    if vin:
        credential_store = CLICredentialStore.get_instance()
        credential_store[CONF_VIN] = Credential(vin)


async def get_locale(websession: aiohttp.ClientSession) -> str:
    """Prompt the user for locale."""
    credential_store = CLICredentialStore.get_instance()
    locale = credential_store.get_value(CONF_LOCALE)
    if locale:
        return locale

    default_locale = getdefaultlocale()[0]
    while True:
        locale = click.prompt("Please select a locale", default=default_locale)
        if locale:
            try:
                await get_api_keys(locale, websession=websession)
            except RenaultException as exc:
                click.echo(str(exc), err=True)
            else:
                if click.confirm(
                    "Do you want to save the locale to the credential store?",
                    default=False,
                ):
                    credential_store[CONF_LOCALE] = Credential(locale)
                return locale
            click.echo(f"Locale `{locale}` is unknown.", err=True)


def display_keys() -> None:
    """Get the current configuration keys."""
    credential_store = CLICredentialStore.get_instance()
    for key in PERMANENT_KEYS:
        click.echo(f"Current {key}: {credential_store.get_value(key)}")
