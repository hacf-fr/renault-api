"""CLI function for a vehicle."""

from typing import Any

import aiohttp
import click
import dateparser

from renault_api.cli import helpers
from renault_api.cli import renault_vehicle


@click.command()
@click.option(
    "--set",
    help="Target charge mode (schedule_mode/always/always_schedule)",
)
@click.pass_obj
@helpers.coro_with_websession
async def mode(
    ctx_data: dict[str, Any],
    *,
    set: str | None = None,
    websession: aiohttp.ClientSession,
) -> None:
    """Display or set charge mode."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    if set:
        write_response = await vehicle.set_charge_mode(set)
        click.echo(write_response.raw_data)
    else:
        read_response = await vehicle.get_charge_mode()
        click.echo(f"Charge mode: {read_response.chargeMode}")


@click.command()
@click.pass_obj
@helpers.coro_with_websession
@click.option(
    "--at",
    default=None,
    help="Date/time at which to start charging."
    " (defaults to immediate if not given). You can use"
    " times like 'in 5 minutes' or 'tomorrow at 9am'.",
)
async def start(
    ctx_data: dict[str, Any],
    *,
    at: str | None,
    websession: aiohttp.ClientSession,
) -> None:
    """Start charging with optional delay."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    if at:
        when = dateparser.parse(at)
    else:
        when = None
    response = await vehicle.set_charge_start(when=when)
    click.echo(response.raw_data)


@click.command()
@click.pass_obj
@helpers.coro_with_websession
async def stop(
    ctx_data: dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Stop charge."""
    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.set_charge_stop()
    click.echo(response.raw_data)
