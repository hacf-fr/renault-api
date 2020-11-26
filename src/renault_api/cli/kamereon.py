"""Singletons for the CLI."""
import aiohttp
import click
from tabulate import tabulate

from .core import CLICredentialStore
from .core import CONF_ACCOUNT_ID
from .core import CONF_VIN
from renault_api.const import CONF_LOCALE
from renault_api.exceptions import RenaultException
from renault_api.helpers import get_api_keys
from renault_api.kamereon import CREDENTIAL_GIGYA_LOGIN_TOKEN
from renault_api.kamereon import Kamereon


class CLIKamereon:
    """Singleton of the CredentialStore for the CLI."""

    __instance: Kamereon = None

    @classmethod
    async def get_instance(
        cls, websession: aiohttp.ClientSession, locale: str
    ) -> Kamereon:
        """Get singleton Kamereon client."""
        if not CLIKamereon.__instance:
            credential_store = CLICredentialStore.get_instance()
            locale = credential_store.get_value(CONF_LOCALE)
            country = locale[-2:]
            api_keys = await get_api_keys(locale, aiohttp_session=websession)
            return Kamereon(
                websession, country, api_keys, credential_store=credential_store
            )
        return CLIKamereon.__instance


async def ensure_logged_in(websession, locale) -> None:
    """Prompt the user for credentials."""
    credential_store = CLICredentialStore.get_instance()
    if CREDENTIAL_GIGYA_LOGIN_TOKEN in credential_store:
        return

    while True:
        user = click.prompt("user")
        password = click.prompt("password", hide_input=True)
        try:
            await do_login(websession, locale, user, password)
        except RenaultException as exc:
            click.echo(f"Login failed: {exc}.", err=True)
        else:
            return


async def do_login(websession, locale, user, password):
    """Attempt login."""
    kamereon = await CLIKamereon.get_instance(websession, locale)
    await kamereon.login(user, password)


async def get_account(websession, locale) -> str:
    """Prompt the user for account."""
    credential_store = CLICredentialStore.get_instance()
    if CONF_ACCOUNT_ID in credential_store:
        return credential_store.get_value(CONF_ACCOUNT_ID)

    await ensure_logged_in(websession, locale)
    kamereon = await CLIKamereon.get_instance(websession, locale)
    response = await kamereon.get_person()
    if not response.accounts:
        raise RenaultException("No account found.")
    if len(response.accounts) == 1:
        return response.accounts[0].accountId
    elif len(response.accounts) > 1:
        menu = "Multiple accounts found:\n"
        for i, account in enumerate(response.accounts):
            menu = menu + f"\t[{i+1}] {account.accountId} ({account.accountType})\n"

        while True:
            i = int(click.prompt(f"{menu}Please select"))
            try:
                account = response.accounts[i - 1].accountId
            except (KeyError, IndexError) as exc:
                click.echo(f"Invalid option: {exc}.", err=True)
            else:
                click.echo(
                    "To avoid seeing this message again, use:"
                    f"> renault-api set --account {account}"
                )
                return account


async def get_vin(websession, locale, account):
    """Prompt the user for vin."""
    credential_store = CLICredentialStore.get_instance()
    if CONF_VIN in credential_store:
        return

    await ensure_logged_in(websession, locale)
    kamereon = await CLIKamereon.get_instance(websession, locale)
    response = await kamereon.get_vehicles(account)
    if not response.vehicleLinks:
        raise RenaultException("No vehicle found.")
    if len(response.vehicleLinks) == 1:
        return response.vehicleLinks[0].vin
    elif len(response.vehicleLinks) > 1:
        menu = "Multiple vehicles found:\n"
        for i, vehicle in enumerate(response.vehicleLinks):
            menu = menu + f"\t[{i+1}] {vehicle.vin}\n"

        while True:
            i = int(click.prompt(f"{menu}Please select"))
            try:
                return response.vehicleLinks[i - 1].vin
            except (KeyError, IndexError) as exc:
                click.echo(f"Invalid option: {exc}.", err=True)


async def display_accounts(websession, locale) -> None:
    """Login to Renault."""
    await ensure_logged_in(websession, locale)
    kamereon = await CLIKamereon.get_instance(websession, locale)
    response = await kamereon.get_person()
    accounts = {account.accountType: account.accountId for account in response.accounts}
    click.echo(tabulate(accounts.items(), headers=["Type", "ID"]))
