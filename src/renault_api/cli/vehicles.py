"""CLI function for a vehicle."""
from typing import cast
from typing import Optional

import aiohttp
import click
from tabulate import tabulate

from .kamereon import CLIKamereon
from .kamereon import ensure_logged_in
from .kamereon import get_account
from renault_api.cli.core import get_locale
from renault_api.kamereon import Kamereon


async def display_vehicles(
    websession: aiohttp.ClientSession, locale: Optional[str], account: Optional[str]
) -> None:
    """Display vehicle status."""
    await ensure_logged_in(websession, locale)

    if not locale:
        locale = await get_locale(websession)
    if not account:
        account = await get_account(websession, locale)

    kamereon = cast(Kamereon, await CLIKamereon.get_client(websession))

    response = await kamereon.get_vehicles(account)
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
