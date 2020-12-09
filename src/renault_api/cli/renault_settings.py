"""Singletons for the CLI."""
import os
from textwrap import TextWrapper
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click
from tabulate import tabulate

from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential_store import CredentialStore
from renault_api.helpers import get_api_keys

CONF_ACCOUNT_ID = "accound-id"
CONF_VIN = "vin"

CREDENTIAL_PATH = "~/.credentials/renault-api.json"


async def set_options(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    locale: Optional[str],
    account: Optional[str],
    vin: Optional[str],
) -> None:
    """Set configuration keys."""
    credential_store: CredentialStore = ctx_data["credential_store"]
    if locale:
        # Ensure API keys are available
        api_keys = await get_api_keys(locale, websession=websession)

        credential_store[CONF_LOCALE] = Credential(locale)
        for k, v in api_keys.items():
            credential_store[k] = Credential(v)

    if account:
        credential_store[CONF_ACCOUNT_ID] = Credential(account)
    if vin:
        credential_store[CONF_VIN] = Credential(vin)


def display_settings(ctx_data: Dict[str, Any]) -> None:
    """Get the current configuration keys."""
    credential_store: CredentialStore = ctx_data["credential_store"]
    wrapper = TextWrapper(width=80)
    items = list(
        [key, "\n".join(wrapper.wrap(credential_store.get_value(key) or "-"))]
        for key in credential_store._store.keys()
    )
    click.echo(tabulate(items, headers=["Key", "Value"]))


def reset() -> None:
    """Clear all credentials/settings from the credential store."""
    try:
        os.remove(os.path.expanduser(CREDENTIAL_PATH))
    except FileNotFoundError:
        pass
