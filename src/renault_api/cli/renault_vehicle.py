"""CLI function for a vehicle."""
from typing import Any, Dict

import aiohttp
import click
import dateparser
import dateutil.parser
from tabulate import tabulate

from . import settings
from . import renault_account
from renault_api.exceptions import KamereonResponseException, RenaultException
from renault_api.renault_account import RenaultAccount
from renault_api.renault_vehicle import RenaultVehicle


async def _get_vin(ctx_data: Dict[str, Any], account: RenaultAccount) -> str:
    """Prompt the user for vin."""
    # First, check context data
    if "vin" in ctx_data:
        return ctx_data["vin"]

    # Second, check credential store
    credential_store = settings.CLICredentialStore.get_instance()
    if settings.CONF_VIN in credential_store:
        return credential_store.get_value(settings.CONF_VIN)

    # Third, prompt the user
    response = await account.get_vehicles()
    if not response.vehicleLinks:
        raise RenaultException("No vehicle found.")
    if len(response.vehicleLinks) == 1:
        return response.vehicleLinks[0].vin
    elif len(response.vehicleLinks) > 1:
        menu = "Multiple vehicles found:\n"
        for i, vehicle in enumerate(response.vehicleLinks):
            menu = menu + f"\t[{i+1}] {vehicle.vin}\n"

        while True:
            i = int(click.prompt(f"{menu}Please select"))
            try:
                return response.vehicleLinks[i - 1].vin
            except (KeyError, IndexError) as exc:
                click.echo(f"Invalid option: {exc}.", err=True)


async def _get_vehicle(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultVehicle:
    account = await renault_account.get_account(
        websession=websession, ctx_data=ctx_data
    )
    vin = await _get_vin(ctx_data, account)
    return await account.get_api_vehicle(vin)


async def ac_start(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    temperature: int,
    at: str,
) -> None:
    """Display vehicle status."""
    vehicle = await _get_vehicle(websession=websession, ctx_data=ctx_data)
    if at:
        when = dateparser.parse(at)
    else:
        when = None
    await vehicle.set_ac_start(temperature=temperature, when=when)


async def display_status(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display vehicle status."""
    vehicle = await _get_vehicle(websession=websession, ctx_data=ctx_data)
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
