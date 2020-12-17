"""CLI function for a vehicle."""
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click
import dateparser

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle


@click.command()
@click.option(
    "--temperature", type=int, help="Target temperature (in Celsius)", required=True
)
@click.option(
    "--at",
    default=None,
    help="Date/time at which to complete preconditioning"
    " (defaults to immediate if not given). You can use"
    " times like 'in 5 minutes' or 'tomorrow at 9am'.",
)
@click.pass_obj
@helpers.coro_with_websession
async def start(
    ctx_data: Dict[str, Any],
    *,
    temperature: int,
    at: Optional[str],
    websession: aiohttp.ClientSession,
) -> None:
    """Start air conditioning."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    if at:
        when = dateparser.parse(at)
    else:
        when = None
    response = await vehicle.set_ac_start(temperature=temperature, when=when)
    click.echo(response.raw_data)


@click.command()
@click.pass_obj
@helpers.coro_with_websession
async def cancel(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Cancel air conditioning."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.set_ac_stop()
    click.echo(response.raw_data)
