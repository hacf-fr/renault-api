"""CLI function for a vehicle."""
from typing import Dict
from typing import Optional

import aiohttp
import click
import dateutil.parser
from tabulate import tabulate

from .core import get_locale
from .kamereon import CLIKamereon
from .kamereon import ensure_logged_in
from .kamereon import get_account
from .kamereon import get_vin
from renault_api.exceptions import KamereonResponseException
from renault_api.renault_vehicle import RenaultVehicle


async def display_status(
    websession: aiohttp.ClientSession,
    locale: Optional[str],
    account: Optional[str],
    vin: Optional[str],
) -> None:
    """Display vehicle status."""
    if not locale:
        locale = await get_locale(websession)
    if not account:
        account = await get_account(websession, locale)
    if not vin:
        vin = await get_vin(websession, locale, account)

    await ensure_logged_in(websession, locale)
    kamereon = await CLIKamereon.get_instance(websession, locale)
    vehicle = RenaultVehicle(kamereon=kamereon, account_id=account, vin=vin)
    status_table = {}

    await update_battery_status(vehicle, status_table)
    await update_charge_mode(vehicle, status_table)
    await update_cockpit(vehicle, status_table)
    await update_location(vehicle, status_table)
    await update_hvac_status(vehicle, status_table)

    click.echo(tabulate(status_table.items()))


async def update_battery_status(
    vehicle: RenaultVehicle, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_battery_status."""
    try:
        response = await vehicle.get_battery_status()
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"battery-status: {exc.error_details}", err=True)
    else:
        if response.batteryLevel is not None:
            status_table["Battery level"] = f"{response.batteryLevel} %"
        if (
            response.batteryAvailableEnergy is not None
            and response.batteryAvailableEnergy > 0
        ):
            status_table["Available energy"] = f"{response.batteryAvailableEnergy} kWh"
        if response.batteryAutonomy is not None:
            status_table["Range estimate"] = f"{response.batteryAutonomy} km"
        if response.plugStatus is not None:
            status_table["Plug state"] = response.get_plug_status().name
        if response.chargingStatus is not None:
            status_table["Charging state"] = response.get_charging_status().name
        if response.chargingInstantaneousPower is not None:
            status_table[
                "Charge rate"
            ] = f"{response.chargingInstantaneousPower:.2f} kW"
        if response.chargingRemainingTime is not None:
            status_table["Time remaining"] = f"{response.chargingRemainingTime} min"


async def update_charge_mode(
    vehicle: RenaultVehicle, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_charge_mode."""
    try:
        response = await vehicle.get_charge_mode()
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"charge-mode: {exc.error_details}", err=True)
    else:
        if response.chargeMode is not None:
            status_table["Charge mode"] = response.chargeMode


async def update_cockpit(vehicle: RenaultVehicle, status_table: Dict[str, str]) -> None:
    """Update status table from get_vehicle_cockpit."""
    try:
        response = await vehicle.get_cockpit()
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"cockpit: {exc.error_details}", err=True)
    else:
        if response.totalMileage is not None:
            status_table["Total mileage"] = f"{response.totalMileage} km"
        if response.fuelAutonomy is not None:
            status_table["Fuel autonomy"] = f"{response.fuelAutonomy} km"
        if response.fuelQuantity is not None:
            status_table["Fuel quantity"] = f"{response.fuelQuantity} L"


async def update_location(
    vehicle: RenaultVehicle, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_location."""
    try:
        response = await vehicle.get_location()
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"location: {exc.error_details}", err=True)
    else:
        if response.gpsLatitude is not None:
            status_table["GPS Latitude"] = response.gpsLatitude
        if response.gpsLongitude is not None:
            status_table["GPS Longitude"] = response.gpsLongitude
        if response.lastUpdateTime is not None:
            status_table["GPS last updated"] = dateutil.parser.parse(
                response.lastUpdateTime
            )


async def update_hvac_status(
    vehicle: RenaultVehicle, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_hvac_status."""
    try:
        response = await vehicle.get_hvac_status()
    except KamereonResponseException as exc:
        if exc.error_code == "err.func.wired.overloaded":
            raise click.ClickException(exc.error_details) from exc
        click.echo(f"hvac-status: {exc.error_details}", err=True)
    else:
        if response.hvacStatus is not None:
            status_table["HVAC status"] = response.hvacStatus
        # Todo: add nextHvacStartDate to KamereonVehicleHvacStatusData
        # if response.nextHvacStartDate is not None:
        #     status_table["HVAC start at"] = dateutil.parser.parse(
        #         response.nextHvacStartDate
        #     )
        if response.externalTemperature is not None:
            status_table["External temperature"] = f"{response.externalTemperature} °C"
