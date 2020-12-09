"""CLI function for a vehicle."""
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click
import dateparser

from . import renault_vehicle
from .helpers import parse_dates


async def start(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    temperature: int,
    at: Optional[str] = None,
) -> None:
    """Start air conditionning."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    if at:
        when = dateparser.parse(at)
    else:
        when = None
    response = await vehicle.set_ac_start(temperature=temperature, when=when)
    click.echo(response.raw_data)


async def cancel(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
) -> None:
    """Cancel air conditionning."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.set_ac_stop()
    click.echo(response.raw_data)


async def history(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
    period: Optional[str] = None,
) -> None:
    """Display vehicle status."""
    parsed_start, parsed_end = parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_hvac_history(
        start=parsed_start, end=parsed_end, period=period
    )
    click.echo(response.raw_data)


async def sessions(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
) -> None:
    """Display vehicle status."""
    parsed_start, parsed_end = parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_hvac_sessions(start=parsed_start, end=parsed_end)
    click.echo(response.raw_data)
