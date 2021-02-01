"""CLI function for a vehicle."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import aiohttp
import click
from tabulate import tabulate

from . import renault_client
from . import renault_settings
from renault_api.credential import Credential
from renault_api.credential_store import CredentialStore
from renault_api.exceptions import RenaultException
from renault_api.kamereon.models import KamereonPersonAccount
from renault_api.renault_account import RenaultAccount
from renault_api.renault_client import RenaultClient


async def _get_account_id(ctx_data: Dict[str, Any], client: RenaultClient) -> str:
    """Prompt the user for account."""
    # First, check context data
    if "account" in ctx_data:
        return str(ctx_data["account"])

    # Second, check credential store
    credential_store: CredentialStore = ctx_data["credential_store"]

    account_id = credential_store.get_value(renault_settings.CONF_ACCOUNT_ID)
    if account_id:
        return account_id

    # Third, prompt the user
    response = await client.get_person()
    if not response.accounts:  # pragma: no cover
        raise RenaultException("No account found.")

    prompt, default = await _get_account_prompt(response.accounts, client)

    while True:
        i = int(
            click.prompt(
                prompt,
                default=default,
                type=click.IntRange(min=1, max=len(response.accounts)),
            )
        )
        try:
            account_id = str(response.accounts[i - 1].accountId)
        except (KeyError, IndexError) as exc:  # pragma: no cover
            click.echo(f"Invalid option: {exc}.", err=True)
        else:
            if click.confirm(  # pragma: no branch
                "Do you want to save the account ID to the credential store?",
                default=False,
            ):
                credential_store[renault_settings.CONF_ACCOUNT_ID] = Credential(
                    account_id
                )
            # Add blank new line
            click.echo("")
            return account_id


async def _get_account_prompt(
    accounts: List[KamereonPersonAccount], client: RenaultClient
) -> Tuple[str, Optional[str]]:
    """Get prompt for selecting account."""
    account_table = []
    default = None
    for i, account in enumerate(accounts):
        if not account.accountId:  # pragma: no cover
            continue
        api_account = await client.get_api_account(account.accountId)
        vehicles = await api_account.get_vehicles()
        if account.accountType == "MYRENAULT":
            default = str(i + 1)
        account_table.append(
            [
                i + 1,
                account.accountId,
                account.accountType,
                0 if vehicles.vehicleLinks is None else len(vehicles.vehicleLinks),
            ]
        )

    menu = tabulate(account_table, headers=["", "ID", "Type", "Vehicles"])
    prompt = f"{menu}\n\nPlease select account"
    return (prompt, default)


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
    if response.vehicleLinks is None:  # pragma: no cover
        raise ValueError("response.vehicleLinks is None")
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
