"""Singletons for the CLI."""
from locale import getdefaultlocale
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click
from tabulate import tabulate

from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential_store import CredentialStore
from renault_api.exceptions import RenaultException
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.helpers import get_api_keys
from renault_api.renault_client import RenaultClient


class CLIClient:
    """Singleton of the RenaultClient for the CLI."""

    __instance: Optional[RenaultClient] = None

    @classmethod
    async def get_instance(
        cls, websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
    ) -> RenaultClient:
        """Get singleton RenaultClient."""
        if not CLIClient.__instance:
            credential_store: CredentialStore = ctx_data["credential_store"]
            locale = ctx_data.get("locale")
            if not locale:
                locale = await get_locale(websession, ctx_data)

            country = locale[-2:]
            api_keys = await get_api_keys(locale=locale, websession=websession)
            return RenaultClient(
                websession=websession,
                locale=locale,
                country=country,
                locale_details=api_keys,
                credential_store=credential_store,
            )
        return CLIClient.__instance


async def get_locale(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> str:
    """Prompt the user for locale."""
    credential_store: CredentialStore = ctx_data["credential_store"]
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


async def get_logged_in_client(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultClient:
    """Get RenaultClient for use by CLI."""
    await _ensure_logged_in(websession, ctx_data)
    return await CLIClient.get_instance(websession, ctx_data)


async def _ensure_logged_in(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Prompt the user for credentials."""
    credential_store: CredentialStore = ctx_data["credential_store"]
    if GIGYA_LOGIN_TOKEN in credential_store:
        return

    while True:
        user = click.prompt("user")
        password = click.prompt("password", hide_input=True)
        try:
            await login(websession, ctx_data, user, password)
        except RenaultException as exc:
            click.echo(f"Login failed: {exc}.", err=True)
        else:
            return


async def login(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    user: str,
    password: str,
) -> None:
    """Attempt login."""
    client = await CLIClient.get_instance(websession=websession, ctx_data=ctx_data)
    await client.session.login(user, password)


async def display_accounts(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display accounts."""
    client = await get_logged_in_client(websession=websession, ctx_data=ctx_data)
    response = await client.get_person()
    accounts = {account.accountType: account.accountId for account in response.accounts}
    click.echo(tabulate(accounts.items(), headers=["Type", "ID"]))
