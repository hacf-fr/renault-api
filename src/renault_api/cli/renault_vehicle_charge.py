"""CLI function for a vehicle."""
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click

from . import renault_vehicle
from .helpers import parse_dates
from renault_api.kamereon.enums import ChargeMode


async def charges(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
) -> None:
    """Display charges."""
    parsed_start, parsed_end = parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charges(start=parsed_start, end=parsed_end)
    click.echo(response.raw_data)


async def history(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
    period: Optional[str] = None,
) -> None:
    """Display charge history."""
    parsed_start, parsed_end = parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charge_history(
        start=parsed_start, end=parsed_end, period=period
    )
    click.echo(response.raw_data)


async def mode(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    mode: Optional[str] = None,
) -> None:
    """Display or set charge mode."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    if mode:
        charge_mode = ChargeMode(mode)
        response = await vehicle.set_charge_mode(charge_mode)
    else:
        response = await vehicle.get_charge_mode()
    click.echo(response.raw_data)


async def settings(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
) -> None:
    """Display charging settings."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charging_settings()
    click.echo(response.raw_data)


async def start(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
) -> None:
    """Start charge."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.set_charge_start()
    click.echo(response.raw_data)
