"""CLI function for a vehicle."""
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle


@click.command()
@helpers.start_end_option(True)
@click.pass_obj
@helpers.coro_with_websession
async def history(
    ctx_data: Dict[str, Any],
    *,
    start: str,
    end: str,
    period: Optional[str],
    websession: aiohttp.ClientSession,
) -> None:
    """Display air conditioning history."""
    parsed_start, parsed_end = helpers.parse_dates(start, end)
    period = period or "month"

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_hvac_history(
        start=parsed_start, end=parsed_end, period=period
    )
    click.echo(response.raw_data)


@click.command()
@helpers.start_end_option(False)
@click.pass_obj
@helpers.coro_with_websession
async def sessions(
    ctx_data: Dict[str, Any],
    *,
    start: str,
    end: str,
    websession: aiohttp.ClientSession,
) -> None:
    """Display air conditioning sessions."""
    parsed_start, parsed_end = helpers.parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_hvac_sessions(start=parsed_start, end=parsed_end)
    click.echo(response.raw_data)
