"""CLI function for a vehicle."""
import dateutil.parser
from typing import Dict
from typing import Optional

import click
from tabulate import tabulate

from .kamereon import CLIKamereon
from .kamereon import ensure_logged_in
from .kamereon import get_account
from .kamereon import get_vin
from renault_api.exceptions import KamereonResponseException


async def display_status(
    websession, account: Optional[str], vin: Optional[str]
) -> None:
    """Display vehicle status."""
    await ensure_logged_in(websession)

    if not account:
        account = await get_account(websession)
    if not vin:
        vin = await get_vin(websession, account)

    kamereon = await CLIKamereon.get_client(websession)
    status_table = {}

    await update_battery_status(kamereon, account, vin, status_table)
    await update_charge_mode(kamereon, account, vin, status_table)
    await update_cockpit(kamereon, account, vin, status_table)
    await update_location(kamereon, account, vin, status_table)
    await update_hvac_status(kamereon, account, vin, status_table)

    click.echo(tabulate(status_table.items()))


async def update_battery_status(
    kamereon, account: str, vin: str, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_battery_status."""
    try:
        response = await kamereon.get_vehicle_battery_status(account, vin)
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"battery-status: {exc.error_details}", err=True)
    else:
        attributes = response.data.raw_data["attributes"]
        status_table["Battery level"] = f"{attributes.get('batteryLevel')} %"
        if attributes.get('batteryAvailableEnergy', 0) > 0:
            status_table[
                "Available energy"
            ] = f"{attributes['batteryAvailableEnergy']} kWh"
        status_table["Range estimate"] = f"{attributes.get('batteryAutonomy')} km"
        status_table["Plug state"] = attributes.get('plugStatus')
        status_table["Charging state"] = attributes.get('chargingStatus')
        status_table["Charge rate"] = attributes.get('chargingStatus')
        if "chargingInstantaneousPower" in attributes:
            status_table["Charge rate"] = f"{attributes['chargingInstantaneousPower']:.2f} kW"
        if "chargingRemainingTime" in attributes:
            status_table['Time remaining'] = f"{attributes['chargingRemainingTime']} min"


async def update_charge_mode(
    kamereon, account: str, vin: str, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_charge_mode."""
    try:
        response = await kamereon.get_vehicle_charge_mode(account, vin)
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"charge-mode: {exc.error_details}", err=True)
    else:
        attributes = response.data.raw_data["attributes"]
        status_table["Charge mode"] = f"{attributes.get('chargeMode')} %"


async def update_cockpit(
    kamereon, account: str, vin: str, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_cockpit."""
    try:
        response = await kamereon.get_vehicle_cockpit(account, vin)
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"cockpit: {exc.error_details}", err=True)
    else:
        attributes = response.data.raw_data["attributes"]
        status_table["Total mileage"] = f"{attributes.get('totalMileage')} km"


async def update_location(
    kamereon, account: str, vin: str, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_location."""
    try:
        response = await kamereon.get_vehicle_location(account, vin)
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"location: {exc.error_details}", err=True)
    else:
        attributes = response.data.raw_data["attributes"]
        if "gpsLatitude" in attributes:
            status_table["GPS Latitude"] = attributes['gpsLatitude']
        if "gpsLongitude" in attributes:
            status_table["GPS Longitude"] = attributes['gpsLongitude']
        if "lastUpdateTime" in attributes:
            status_table["GPS last updated"] = dateutil.parser.parse(
                attributes["lastUpdateTime"])


async def update_hvac_status(
    kamereon, account: str, vin: str, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_hvac_status."""
    try:
        response = await kamereon.get_vehicle_hvac_status(account, vin)
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"hvac-status: {exc.error_details}", err=True)
    else:
        attributes = response.data.raw_data["attributes"]
        if "hvacStatus" in attributes:
            status_table["AC state"] = attributes['hvacStatus']
        if "nextHvacStartDate" in attributes:
            status_table["AC start at"] = dateutil.parser.parse(
                attributes["nextHvacStartDate"])
        if "externalTemperature" in attributes:
            status_table["External temperature"] = f"{attributes['externalTemperature']} °C"
