"""CLI function for a vehicle."""

from typing import Any

import aiohttp
import click

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle

# SoC level boundaries (to comply with mobile apps contraints and to
# balance poor Renault API checks)
MIN_SOC_MIN = 15
MAX_SOC_MIN = 45
MIN_SOC_TARGET = 55
MAX_SOC_TARGET = 100
SOC_STEP = 5


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

    if min < MIN_SOC_MIN or min > MAX_SOC_MIN or min % SOC_STEP != 0:
        raise click.BadParameter(
            f"Minimum state of charge level must be between {MIN_SOC_MIN} and "
            f"{MAX_SOC_MIN} with a step of {SOC_STEP}."
        )
    if target < MIN_SOC_TARGET or target > MAX_SOC_TARGET or target % SOC_STEP != 0:
        raise click.BadParameter(
            f"Target state of charge level must be between {MIN_SOC_TARGET} and "
            f"{MAX_SOC_TARGET} with a step of {SOC_STEP}."
        )

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )

    await vehicle.set_battery_soc(
        min=min if min is not None else 0,
        target=target if target is not None else 0,
    )
    click.echo(
        f"Charge soc levels updated to {min}-{target} successfully. "
        "It may take up to a few minutes to apply."
    )
