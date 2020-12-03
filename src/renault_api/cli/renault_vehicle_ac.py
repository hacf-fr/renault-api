"""CLI function for a vehicle."""
from datetime import datetime
from typing import Any
from typing import Dict

import aiohttp
import click
import dateparser
from tabulate import tabulate

from . import renault_vehicle
from renault_api.credential import Credential
from renault_api.exceptions import RenaultException
from renault_api.renault_account import RenaultAccount
from renault_api.renault_vehicle import RenaultVehicle


async def start(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    temperature: int,
    at: str,
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
    period: str,
) -> None:
    """Display vehicle status."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_hvac_history(
        start=dateparser.parse(start), end=dateparser.parse(end), period=period
    )
    click.echo(response.raw_data)


async def sessions(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
) -> None:
    """Display vehicle status."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_hvac_sessions(
        start=dateparser.parse(start), end=dateparser.parse(end)
    )
    click.echo(response.raw_data)
