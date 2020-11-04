"""CLI function for a vehicle."""
from typing import Optional

import click
from tabulate import tabulate

from .kamereon import CLIKamereon
from .kamereon import ensure_logged_in
from .kamereon import get_account


async def display_vehicles(
    websession, account: Optional[str]
) -> None:
    """Display vehicle status."""
    await ensure_logged_in(websession)

    if not account:
        account = await get_account(websession)

    kamereon = await CLIKamereon.get_client(websession)

    response = await kamereon.get_vehicles(account)
    vehicles = [
        [
            vehicle.raw_data['vehicleDetails']['registrationNumber'],
            vehicle.raw_data['vehicleDetails']['brand']['label'],
            vehicle.raw_data['vehicleDetails']['model']['label'],
            vehicle.vin,
        ] for vehicle in response.vehicleLinks]
    click.echo(tabulate(vehicles, headers=[
               "Registration", "Brand", "Model", "VIN"]))
