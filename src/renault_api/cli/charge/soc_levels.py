"""CLI function for a vehicle."""

from typing import Any

import aiohttp
import click

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle


@click.group()
def soclevels() -> None:
    """Display or update charge SoC levels."""
    pass


@soclevels.command()
@click.pass_obj
@helpers.coro_with_websession
async def show(
    ctx_data: dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Display battery soc levels."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )

    read_response = await vehicle.get_battery_soc()

    click.echo(f"Min charge level: {read_response.socMin}%")
    click.echo(f"Max charge level: {read_response.socTarget}%")


@soclevels.command()
@click.option(
    "--min", type=int, help="Minimum state of charge level to set", required=True
)
@click.option(
    "--max", type=int, help="Maximum state of charge level to set", required=True
)
@click.pass_obj
@helpers.coro_with_websession
async def set(
    ctx_data: dict[str, Any],
    *,
    min: int,
    max: int,
    websession: aiohttp.ClientSession,
) -> None:
    """Display or set battery soc levels."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )

    await vehicle.set_battery_soc(
        min_level=min if min is not None else 0,
        target_level=max if max is not None else 0,
    )
    click.echo(
        "Charge soc levels updated successfully. "
        "It may take up to a few minutes to apply."
    )
