"""CLI function for a vehicle."""
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import aiohttp
import click
from tabulate import tabulate

from . import helpers
from . import renault_vehicle
from renault_api.kamereon.enums import ChargeMode


async def charges(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
) -> None:
    """Display charges."""
    parsed_start, parsed_end = helpers.parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charges(start=parsed_start, end=parsed_end)
    charges: List[Dict[str, Any]] = response.raw_data["charges"]
    if not charges:
        click.echo("No data available.")
        return

    headers = [
        "Charge start",
        "Charge end",
        "Duration",
        "Power (kW)",
        "Started at",
        "Finished at",
        "Charge gained",
        "Power level",
        "Status",
    ]
    click.echo(
        tabulate([_format_charges_item(item) for item in charges], headers=headers)
    )


def _format_charges_item(item: Dict[str, Any]) -> List[str]:
    return [
        helpers.get_display_value(item.get("chargeStartDate"), "datetime"),
        helpers.get_display_value(item.get("chargeEndDate"), "datetime"),
        helpers.get_display_value(item.get("chargeDuration"), "minutes"),
        helpers.get_display_value(item.get("chargeStartInstantaneousPower"), "kW"),
        helpers.get_display_value(item.get("chargeStartBatteryLevel"), "%"),
        helpers.get_display_value(item.get("chargeEndBatteryLevel"), "%"),
        helpers.get_display_value(item.get("chargeBatteryLevelRecovered"), "%"),
        helpers.get_display_value(item.get("chargePower")),
        helpers.get_display_value(item.get("chargeEndStatus")),
    ]


async def history(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    start: str,
    end: str,
    period: Optional[str] = None,
) -> None:
    """Display charge history."""
    parsed_start, parsed_end = helpers.parse_dates(start, end)

    vehicle = await renault_vehicle.get_vehicle(
        websession=websession, ctx_data=ctx_data
    )
    response = await vehicle.get_charge_history(
        start=parsed_start, end=parsed_end, period=period
    )
    charge_summaries: List[Dict[str, Any]] = response.raw_data["chargeSummaries"]
    if not charge_summaries:
        click.echo("No data available.")
        return

    headers = [
        period.capitalize(),
        "Number of charges",
        "Total time charging",
        "Errors",
    ]
    click.echo(
        tabulate(
            [_format_charge_history_item(item, period) for item in charge_summaries],
            headers=headers,
        )
    )


def _format_charge_history_item(item: Dict[str, Any], period: str) -> List[str]:
    return [
        helpers.get_display_value(item.get(period)),
        helpers.get_display_value(item.get("totalChargesNumber")),
        helpers.get_display_value(item.get("totalChargesDuration"), "minutes"),
        helpers.get_display_value(item.get("totalChargesErrors")),
    ]


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
        click.echo(response.raw_data)
    else:
        response = await vehicle.get_charge_mode()
        display_data = [("Charge mode", response.chargeMode)]
        click.echo(tabulate(display_data))


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
