"""CLI function for a vehicle."""
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click
import dateutil.parser
from tabulate import tabulate

from . import renault_account
from . import renault_settings
from renault_api.credential import Credential
from renault_api.credential_store import CredentialStore
from renault_api.exceptions import RenaultException
from renault_api.kamereon.exceptions import KamereonResponseException
from renault_api.kamereon.exceptions import QuotaLimitException
from renault_api.renault_account import RenaultAccount
from renault_api.renault_vehicle import RenaultVehicle


async def _get_vin(ctx_data: Dict[str, Any], account: RenaultAccount) -> str:
    """Prompt the user for vin."""
    # First, check context data
    if "vin" in ctx_data:
        return str(ctx_data["vin"])

    # Second, check credential store
    credential_store: CredentialStore = ctx_data["credential_store"]

    vin = credential_store.get_value(renault_settings.CONF_VIN)
    if vin:
        return vin

    # Third, prompt the user
    response = await account.get_vehicles()
    if not response.vehicleLinks:
        raise RenaultException("No vehicle found.")

    vehicle_table = []
    default = None
    for i, vehicle in enumerate(response.vehicleLinks):
        vehicle_details = vehicle.vehicleDetails
        assert vehicle_details  # noqa: S101
        vehicle_table.append(
            [
                i + 1,
                vehicle_details.vin,
                vehicle_details.registrationNumber,
                vehicle_details.get_brand_label(),
                vehicle_details.get_model_label(),
            ]
        )

    if len(vehicle_table) == 1:
        default = "1"
    menu = tabulate(
        vehicle_table, headers=["", "Vin", "Registration", "Brand", "Model"]
    )
    prompt = f"\n{menu}\n\nPlease select vehicle"

    while True:
        i = int(
            click.prompt(
                prompt,
                default=default,
                type=click.IntRange(min=1, max=len(response.vehicleLinks)),
            )
        )
        try:
            vin = str(response.vehicleLinks[i - 1].vin)
        except (KeyError, IndexError) as exc:
            click.echo(f"Invalid option: {exc}.", err=True)
        else:
            if click.confirm(
                "Do you want to save the VIN to the credential store?",
                default=False,
            ):
                credential_store[renault_settings.CONF_VIN] = Credential(vin)
            return vin


async def get_vehicle(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultVehicle:
    """Get RenaultVehicle for use by CLI."""
    account = await renault_account.get_account(websession, ctx_data)
    vin = await _get_vin(ctx_data, account)
    return await account.get_api_vehicle(vin)


async def display_status(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display vehicle status."""
    vehicle = await get_vehicle(websession, ctx_data)
    status_table: Dict[str, Any] = {}

    await update_battery_status(vehicle, status_table)
    await update_charge_mode(vehicle, status_table)
    await update_cockpit(vehicle, status_table)
    await update_location(vehicle, status_table)
    await update_hvac_status(vehicle, status_table)

    click.echo(tabulate(status_table.items()))


def update_status_table(
    status_table: Dict[str, Any],
    key: str,
    value: Optional[Any],
    unit: Optional[str],
) -> None:
    """Update statuses with formatted strings."""
    if value is None:
        return
    if unit == "datetime":
        unit = None
        value = dateutil.parser.parse(value)
    if unit is None:
        status_table[key] = value
    else:
        status_table[key] = "{0} {1}".format(value, unit)


async def update_battery_status(
    vehicle: RenaultVehicle, status_table: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_battery_status."""
    try:
        response = await vehicle.get_battery_status()
    except QuotaLimitException as exc:
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:
        click.echo(f"battery-status: {exc.error_details}", err=True)
    else:
        if response.batteryAvailableEnergy == 0:
            response.batteryAvailableEnergy = None
        if response.chargingStatus == -1.0 and response.plugStatus == 0:
            response.chargingStatus = 0.0

        items = [
            ("Battery level", response.batteryLevel, "%"),
            ("Last updated", response.timestamp, "datetime"),
            ("Available energy", response.batteryAvailableEnergy, "kWh"),
            ("Range estimate", response.batteryAutonomy, "km"),
            ("Plug state", response.get_plug_status(), None),
            ("Charging state", response.get_charging_status(), None),
            ("Charge rate", response.chargingInstantaneousPower, "kW"),
            ("Time remaining", response.chargingRemainingTime, "min"),
        ]

        for key, value, unit in items:
            update_status_table(status_table, key, value, unit)


async def update_charge_mode(
    vehicle: RenaultVehicle, status_table: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_charge_mode."""
    try:
        response = await vehicle.get_charge_mode()
    except QuotaLimitException as exc:
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:
        click.echo(f"charge-mode: {exc.error_details}", err=True)
    else:
        items = [("Charge mode", response.chargeMode, None)]

        for key, value, unit in items:
            update_status_table(status_table, key, value, unit)


async def update_cockpit(vehicle: RenaultVehicle, status_table: Dict[str, Any]) -> None:
    """Update status table from get_vehicle_cockpit."""
    try:
        response = await vehicle.get_cockpit()
    except QuotaLimitException as exc:
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:
        click.echo(f"cockpit: {exc.error_details}", err=True)
    else:
        items = [
            ("Total mileage", response.totalMileage, "km"),
            ("Fuel autonomy", response.fuelAutonomy, "km"),
            ("Fuel quantity", response.fuelQuantity, "L"),
        ]

        for key, value, unit in items:
            update_status_table(status_table, key, value, unit)


async def update_location(
    vehicle: RenaultVehicle, status_table: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_location."""
    try:
        response = await vehicle.get_location()
    except QuotaLimitException as exc:
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:
        click.echo(f"location: {exc.error_details}", err=True)
    else:
        items = [
            ("GPS Latitude", response.gpsLatitude, None),
            ("GPS Longitude", response.gpsLongitude, None),
            ("GPS last updated", response.lastUpdateTime, "datetime"),
        ]

        for key, value, unit in items:
            update_status_table(status_table, key, value, unit)


async def update_hvac_status(
    vehicle: RenaultVehicle, status_table: Dict[str, str]
) -> None:
    """Update status table from get_vehicle_hvac_status."""
    try:
        response = await vehicle.get_hvac_status()
    except QuotaLimitException as exc:
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:
        click.echo(f"hvac-status: {exc.error_details}", err=True)
    else:
        items = [
            ("HVAC status", response.hvacStatus, None),
            ("HVAC start at", response.nextHvacStartDate, "datetime"),
            ("External temperature", response.externalTemperature, "°C"),
        ]

        for key, value, unit in items:
            update_status_table(status_table, key, value, unit)
