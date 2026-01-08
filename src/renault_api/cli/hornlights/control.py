"""CLI function for a vehicle."""

from typing import Any

import aiohttp
import click

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle


@click.command()
@click.pass_obj
@helpers.coro_with_websession
async def lights(
    ctx_data: dict[str, Any],
    websession: aiohttp.ClientSession,
) -> None:
    """Start lights."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    await vehicle.start_lights()
    click.echo(
        "Request to flash lights 3 times has been sent. "
        "It may take a few seconds to take effect."
    )


@click.command()
@click.pass_obj
@helpers.coro_with_websession
async def horn(
    ctx_data: dict[str, Any],
    websession: aiohttp.ClientSession,
) -> None:
    """Start horn."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    await vehicle.start_horn()
    click.echo(
        "Request to horn 3 times sent. "
        "It may take a few seconds to take effect."
    )
