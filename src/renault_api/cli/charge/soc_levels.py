"""CLI function for a vehicle."""

from typing import Any

import aiohttp
import click

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle
from renault_api.exceptions import InvalidInputError
from renault_api.helpers import validate_battery_soc_input


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
    click.echo(f"Target charge level: {read_response.socTarget}%")


@soclevels.command()
@click.option(
    "--min", type=int, help="Minimum state of charge level to set", required=True
)
@click.option(
    "--target", type=int, help="Target state of charge level to set", required=True
)
@click.pass_obj
@helpers.coro_with_websession
async def set(
    ctx_data: dict[str, Any],
    *,
    min: int,
    target: int,
    websession: aiohttp.ClientSession,
) -> None:
    """Set battery soc levels."""
    try:
        validate_battery_soc_input(min=min, target=target)
    except InvalidInputError as err:
        raise click.BadParameter(getattr(err, "message", str(err))) from err

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )

    await vehicle.set_battery_soc(min=min, target=target)
    click.echo(
        f"Charge soc levels updated to {min}-{target} successfully. "
        "It may take up to a few minutes to apply."
    )
