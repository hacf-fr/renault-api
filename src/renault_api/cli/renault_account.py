"""CLI function for a vehicle."""
from typing import Any
from typing import Dict

import aiohttp
import click
from tabulate import tabulate

from . import renault_client
from . import settings
from renault_api.exceptions import RenaultException
from renault_api.renault_account import RenaultAccount
from renault_api.renault_client import RenaultClient


async def _get_account_id(ctx_data: Dict[str, Any], client: RenaultClient) -> str:
    """Prompt the user for account."""
    # First, check context data
    if "account" in ctx_data:
        return str(ctx_data["account"])

    # Second, check credential store
    credential_store = settings.CLICredentialStore.get_instance()
    account_id = credential_store.get_value(settings.CONF_ACCOUNT_ID)
    if account_id:
        return account_id

    # Third, prompt the user
    response = await client.get_person()
    if not response.accounts:
        raise RenaultException("No account found.")
    if len(response.accounts) == 1:
        return str(response.accounts[0].accountId)
    elif len(response.accounts) > 1:
        menu = "Multiple accounts found:\n"
        for i, account in enumerate(response.accounts):
            menu = menu + f"\t[{i+1}] {account.accountId} ({account.accountType})\n"

        while True:
            i = int(click.prompt(f"{menu}Please select"))
            try:
                account_id = str(response.accounts[i - 1].accountId)
            except (KeyError, IndexError) as exc:
                click.echo(f"Invalid option: {exc}.", err=True)
            else:
                click.echo(
                    "To avoid seeing this message again, use:"
                    f" > renault-api set --account {account_id}"
                )
                return account_id

    raise RenaultException("Unable to get account_id.")  # Unreachable


async def get_account(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultAccount:
    """Get RenaultAccount for use by CLI."""
    client = await renault_client.get_logged_in_client(
        websession=websession, ctx_data=ctx_data
    )
    account_id = await _get_account_id(ctx_data, client)
    return await client.get_api_account(account_id)


async def display_vehicles(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display vehicle status."""
    account = await get_account(websession, ctx_data)

    response = await account.get_vehicles()
    vehicles = [
        [
            vehicle.raw_data["vehicleDetails"]["registrationNumber"],
            vehicle.raw_data["vehicleDetails"]["brand"]["label"],
            vehicle.raw_data["vehicleDetails"]["model"]["label"],
            vehicle.vin,
        ]
        for vehicle in response.vehicleLinks
    ]
    click.echo(tabulate(vehicles, headers=["Registration", "Brand", "Model", "VIN"]))
