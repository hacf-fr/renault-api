"""Singletons for the CLI."""
import aiohttp
import click
from tabulate import tabulate
from typing import Any, Dict

from . import settings
from renault_api.const import CONF_LOCALE
from renault_api.exceptions import RenaultException
from renault_api.helpers import get_api_keys
from renault_api.kamereon import CREDENTIAL_GIGYA_LOGIN_TOKEN
from renault_api.renault_client import RenaultClient


class CLIClient:
    """Singleton of the RenaultClient for the CLI."""

    __instance: RenaultClient = None

    @classmethod
    async def get_instance(
        cls, websession: aiohttp.ClientSession, locale: str
    ) -> RenaultClient:
        """Get singleton RenaultClient."""
        if not CLIClient.__instance:
            credential_store = settings.CLICredentialStore.get_instance()
            locale = credential_store.get_value(CONF_LOCALE)
            country = locale[-2:]
            api_keys = await get_api_keys(locale, aiohttp_session=websession)
            return RenaultClient(
                websession,
                locale,
                country=country,
                locale_details=api_keys,
                credential_store=credential_store,
            )
        return CLIClient.__instance


async def get_logged_in_client(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultClient:
    locale = ctx_data.get("locale")
    if not locale:
        locale = await settings.get_locale(websession)

    await _ensure_logged_in(websession, locale)
    return await CLIClient.get_instance(websession, locale)


async def _ensure_logged_in(websession, locale) -> None:
    """Prompt the user for credentials."""
    credential_store = settings.CLICredentialStore.get_instance()
    if CREDENTIAL_GIGYA_LOGIN_TOKEN in credential_store:
        return

    while True:
        user = click.prompt("user")
        password = click.prompt("password", hide_input=True)
        try:
            await _do_login(websession, locale, user, password)
        except RenaultException as exc:
            click.echo(f"Login failed: {exc}.", err=True)
        else:
            return


async def _do_login(websession, locale, user, password):
    """Attempt login."""
    client = await CLIClient.get_instance(websession, locale)
    await client.login(user, password)


async def display_accounts(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display accounts."""
    client = await get_logged_in_client(websession=websession, ctx_data=ctx_data)
    response = await client.get_person()
    accounts = {account.accountType: account.accountId for account in response.accounts}
    click.echo(tabulate(accounts.items(), headers=["Type", "ID"]))
