"""CLI function for a vehicle."""
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import aiohttp
import click
from tabulate import tabulate

from . import helpers
from . import renault_account
from . import renault_settings
from renault_api.credential import Credential
from renault_api.credential_store import CredentialStore
from renault_api.exceptions import RenaultException
from renault_api.kamereon.exceptions import KamereonResponseException
from renault_api.kamereon.exceptions import QuotaLimitException
from renault_api.kamereon.models import KamereonVehiclesLink
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
    if not response.vehicleLinks:  # pragma: no cover
        raise RenaultException("No vehicle found.")

    prompt, default = await _get_vehicle_prompt(response.vehicleLinks, account)

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
        except (KeyError, IndexError) as exc:  # pragma: no cover
            click.echo(f"Invalid option: {exc}.", err=True)
        else:
            if click.confirm(  # pragma: no branch
                "Do you want to save the VIN to the credential store?",
                default=False,
            ):
                credential_store[renault_settings.CONF_VIN] = Credential(vin)
            click.echo("")
            return vin


async def _get_vehicle_prompt(
    vehicle_links: List[KamereonVehiclesLink], account: RenaultAccount
) -> Tuple[str, Optional[str]]:
    """Get prompt for selecting vehicle."""
    vehicle_table = []
    default = None
    for i, vehicle in enumerate(vehicle_links):
        if not vehicle.vehicleDetails:  # pragma: no cover
            continue
        vehicle_details = vehicle.vehicleDetails
        vehicle_table.append(
            [
                i + 1,
                vehicle_details.vin,
                vehicle_details.registrationNumber,
                vehicle_details.get_brand_label(),
                vehicle_details.get_model_label(),
            ]
        )

    if len(vehicle_table) == 1:  # pragma: no branch
        default = "1"
    menu = tabulate(
        vehicle_table, headers=["", "Vin", "Registration", "Brand", "Model"]
    )
    prompt = f"{menu}\n\nPlease select vehicle"
    return (prompt, default)


async def get_vehicle(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultVehicle:
    """Get RenaultVehicle for use by CLI."""
    account = await renault_account.get_account(websession, ctx_data)
    vin = await _get_vin(ctx_data, account)
    return await account.get_api_vehicle(vin)


async def display_vehicle(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display vehicle status."""
    vehicle = await get_vehicle(websession, ctx_data)
    response = await vehicle.get_details()

    vehicles = [
        [
            response.raw_data["registrationNumber"],
            response.raw_data["brand"]["label"],
            response.raw_data["model"]["label"],
            response.vin,
        ]
    ]

    click.echo(tabulate(vehicles, headers=["Registration", "Brand", "Model", "VIN"]))


async def display_contracts(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display vehicle contracts."""
    vehicle = await get_vehicle(websession, ctx_data)
    response = await vehicle.get_contracts()

    contracts = [
        [
            contract.type,
            contract.code,
            contract.description,
            contract.startDate,
            contract.endDate,
            contract.statusLabel,
        ]
        for contract in response
    ]
    click.echo(
        tabulate(
            contracts, headers=["Type", "Code", "Description", "Start", "End", "Status"]
        )
    )


async def display_status(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display vehicle status."""
    vehicle = await get_vehicle(websession, ctx_data)
    status_table: Dict[str, Any] = {}

    await update_battery_status(vehicle, status_table, ctx_data)
    await update_charge_mode(vehicle, status_table, ctx_data)
    await update_cockpit(vehicle, status_table, ctx_data)
    await update_location(vehicle, status_table, ctx_data)
    await update_lock_status(vehicle, status_table, ctx_data)
    await update_res_state(vehicle, status_table, ctx_data)
    await update_hvac_status(vehicle, status_table, ctx_data)
    if ctx_data["json"]:
        click.echo(json.dumps(status_table))
        return

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
    status_table[key] = helpers.get_display_value(value, unit)


async def update_battery_status(
    vehicle: RenaultVehicle, status_table: Dict[str, Any], ctx_data: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_battery_status."""
    try:
        if not (await vehicle.get_details()).uses_electricity():
            return
        if not await vehicle.supports_endpoint("battery-status"):  # pragma: no cover
            return
        response = await vehicle.get_battery_status()
    except QuotaLimitException as exc:  # pragma: no cover
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:  # pragma: no cover
        click.echo(f"battery-status: {exc.error_details}", err=True)
        return

    if response.batteryAvailableEnergy == 0:  # pragma: no branch
        response.batteryAvailableEnergy = None
    if (  # pragma: no branch
        response.chargingStatus == -1.0 and response.plugStatus == 0
    ):
        response.chargingStatus = 0.0

    if ctx_data["json"]:
        status_table["battery-status"] = response.raw_data
        return
    items = [
        ("Battery level", response.batteryLevel, "%"),
        ("Last updated", response.timestamp, "tzdatetime"),
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
    vehicle: RenaultVehicle, status_table: Dict[str, Any], ctx_data: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_charge_mode."""
    try:
        if not (await vehicle.get_details()).uses_electricity():
            return
        if not await vehicle.supports_endpoint("charge-mode"):  # pragma: no cover
            return
        response = await vehicle.get_charge_mode()
    except QuotaLimitException as exc:  # pragma: no cover
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:  # pragma: no cover
        click.echo(f"charge-mode: {exc.error_details}", err=True)
        return

    if ctx_data["json"]:
        status_table["charge-mode"] = response.raw_data
        return
    items = [("Charge mode", response.chargeMode, None)]

    for key, value, unit in items:
        update_status_table(status_table, key, value, unit)


async def update_cockpit(
    vehicle: RenaultVehicle, status_table: Dict[str, Any], ctx_data: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_cockpit."""
    try:
        if not await vehicle.supports_endpoint("cockpit"):  # pragma: no cover
            return
        response = await vehicle.get_cockpit()
    except QuotaLimitException as exc:  # pragma: no cover
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:  # pragma: no cover
        click.echo(f"cockpit: {exc.error_details}", err=True)
        return

    if ctx_data["json"]:
        status_table["cockpit"] = response.raw_data
        return
    items = [
        ("Total mileage", response.totalMileage, "km"),
        ("Fuel autonomy", response.fuelAutonomy, "km"),
        ("Fuel quantity", response.fuelQuantity, "L"),
    ]

    for key, value, unit in items:
        update_status_table(status_table, key, value, unit)


async def update_location(
    vehicle: RenaultVehicle, status_table: Dict[str, Any], ctx_data: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_location."""
    try:
        if not await vehicle.supports_endpoint("location"):
            return
        response = await vehicle.get_location()
    except QuotaLimitException as exc:  # pragma: no cover
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:  # pragma: no cover
        click.echo(f"location: {exc.error_details}", err=True)
        return

    if ctx_data["json"]:  # pragma: no cover
        status_table["location"] = response.raw_data
        return
    items = [
        ("GPS Latitude", response.gpsLatitude, None),
        ("GPS Longitude", response.gpsLongitude, None),
        ("GPS last updated", response.lastUpdateTime, "tzdatetime"),
    ]

    for key, value, unit in items:
        update_status_table(status_table, key, value, unit)


async def update_lock_status(
    vehicle: RenaultVehicle, status_table: Dict[str, Any], ctx_data: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_lock_status."""
    try:
        if not await vehicle.supports_endpoint("lock-status"):
            return
        response = await vehicle.get_lock_status()
    except QuotaLimitException as exc:  # pragma: no cover
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:  # pragma: no cover
        click.echo(f"lock status: {exc.error_details}", err=True)
        return

    if ctx_data["json"]:  # pragma: no cover
        status_table["lock-status"] = response.raw_data
        return
    items = [
        ("Lock status", response.lockStatus, None),
        ("Lock last updated", response.lastUpdateTime, "tzdatetime"),
    ]

    for key, value, unit in items:
        update_status_table(status_table, key, value, unit)


async def update_res_state(
    vehicle: RenaultVehicle, status_table: Dict[str, Any], ctx_data: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_res_state."""
    try:
        if not await vehicle.supports_endpoint("res-state"):  # pragma: no cover
            return
        response = await vehicle.get_res_state()
    except QuotaLimitException as exc:  # pragma: no cover
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:  # pragma: no cover
        click.echo(f"res state: {exc.error_details}", err=True)
        return

    if ctx_data["json"]:
        status_table["res-state"] = response.raw_data
        return
    items = [
        ("Engine state", response.details, None),
    ]

    for key, value, unit in items:
        update_status_table(status_table, key, value, unit)


async def update_hvac_status(
    vehicle: RenaultVehicle, status_table: Dict[str, Any], ctx_data: Dict[str, Any]
) -> None:
    """Update status table from get_vehicle_hvac_status."""
    try:
        if not await vehicle.supports_endpoint("hvac-status"):
            return
        response = await vehicle.get_hvac_status()
    except QuotaLimitException as exc:  # pragma: no cover
        raise click.ClickException(repr(exc)) from exc
    except KamereonResponseException as exc:  # pragma: no cover
        click.echo(f"hvac-status: {exc.error_details}", err=True)
        return

    if ctx_data["json"]:
        status_table["hvac-status"] = response.raw_data
        return
    items = [
        ("HVAC status", response.hvacStatus, None),
        ("HVAC start at", response.nextHvacStartDate, "tzdatetime"),
        ("External temperature", response.externalTemperature, "°C"),
    ]

    for key, value, unit in items:
        update_status_table(status_table, key, value, unit)
