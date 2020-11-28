"""Kamereon client for interaction with Renault servers."""
import logging
from typing import Any
from typing import cast
from typing import Dict
from typing import Optional

import aiohttp
from marshmallow.schema import Schema

from . import models
from . import schemas


_LOGGER = logging.getLogger(__name__)


def get_commerce_url(root_url: str) -> str:
    """Get the base Kamereon url."""
    return f"{root_url}/commerce/v1"


def get_person_url(root_url: str, person_id: str) -> str:
    """Get the url to the person."""
    return f"{get_commerce_url(root_url)}/persons/{person_id}"


def get_account_url(root_url: str, account_id: str) -> str:
    """Get the url to the account."""
    return f"{get_commerce_url(root_url)}/accounts/{account_id}"


def get_car_adapter_url(root_url: str, account_id: str, version: int, vin: str) -> str:
    """Get the url to the car adapter."""
    account_url = get_account_url(root_url, account_id)
    return f"{account_url}/kamereon/kca/car-adapter/v{version}/cars/{vin}"


async def request(
    websession: aiohttp.ClientSession,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    schema: Optional[Schema] = None,
) -> models.KamereonResponse:
    """Process Kamereon HTTP request."""
    schema = schema or schemas.KamereonResponseSchema
    async with websession.request(
        method,
        url,
        headers=headers,
        params=params,
        data=data,
    ) as http_response:
        response_text = await http_response.text()
        _LOGGER.debug(
            "Received Kamereon response %s on %s: %s",
            http_response.status,
            http_response.url,
            response_text,
        )
        kamereon_response: models.KamereonResponse = schema.loads(response_text)
        # Check for Kamereon error
        kamereon_response.raise_for_error_code()
        # Check for HTTP error
        http_response.raise_for_status()

        return kamereon_response


async def get_person(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    person_id: str,
) -> models.KamereonPersonResponse:
    """GET to /persons/{person_id}."""
    url = get_person_url(root_url, person_id)
    headers = {
        "apikey": api_key,
        "x-gigya-id_token": gigya_jwt,
    }
    params = {"country": country}
    return cast(
        models.KamereonPersonResponse,
        await request(
            websession,
            "GET",
            url,
            headers=headers,
            params=params,
            schema=schemas.KamereonPersonResponseSchema,
        ),
    )


async def get_vehicles(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
) -> models.KamereonVehiclesResponse:
    """GET to /accounts/{account_id}/vehicles."""
    url = f"{get_account_url(root_url, account_id)}/vehicles"
    headers = {
        "apikey": api_key,
        "x-gigya-id_token": gigya_jwt,
    }
    params = {"country": country}
    return cast(
        models.KamereonVehiclesResponse,
        await request(
            websession,
            "GET",
            url,
            headers=headers,
            params=params,
            schema=schemas.KamereonVehiclesResponseSchema,
        ),
    )


async def get_vehicle_data(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    endpoint_version: int,
    vin: str,
    endpoint: str,
    params: Optional[Dict[str, str]] = None,
) -> models.KamereonVehicleDataResponse:
    """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
    car_adapter_url = get_car_adapter_url(root_url, account_id, endpoint_version, vin)
    url = f"{car_adapter_url}/{endpoint}"
    headers = {
        "apikey": api_key,
        "x-gigya-id_token": gigya_jwt,
    }
    params = params or {}
    params["country"] = country
    return cast(
        models.KamereonVehicleDataResponse,
        await request(
            websession,
            "GET",
            url,
            headers=headers,
            params=params,
            schema=schemas.KamereonVehicleDataResponseSchema,
        ),
    )


async def get_vehicle_battery_status_v2(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/battery-status."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        2,
        vin,
        "battery-status",
    )


async def get_vehicle_location(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/location."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "location",
    )


async def get_vehicle_hvac_status(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/hvac-status."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "hvac-status",
    )


async def get_vehicle_charge_mode(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/charge-mode."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "charge-mode",
    )


async def get_vehicle_cockpit(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/cockpit."""
    return await get_vehicle_data(
        websession, root_url, api_key, gigya_jwt, country, account_id, 2, vin, "cockpit"
    )


async def get_vehicle_lock_status(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/lock-status."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "lock-status",
    )


async def get_vehicle_charging_settings(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/charging-settings."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "charging-settings",
    )


async def get_vehicle_notification_settings(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/notification-settings."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "notification-settings",
    )


async def get_vehicle_charges(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    params: Dict[str, str],
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/charges."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "charges",
        params,
    )


async def get_vehicle_charge_history(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    params: Dict[str, str],
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/charge-history."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "charge-history",
        params,
    )


async def get_vehicle_hvac_sessions(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    params: Dict[str, str],
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/hvac-sessions."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "hvac-sessions",
        params,
    )


async def get_vehicle_hvac_history(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    params: Dict[str, str],
) -> models.KamereonVehicleDataResponse:
    """GET to /cars/{vin}/hvac-history."""
    return await get_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "hvac-history",
        params,
    )


async def set_vehicle_data(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    endpoint_version: int,
    vin: str,
    endpoint: str,
    data: Dict[str, Any],
) -> models.KamereonVehicleDataResponse:
    """POST to /v{endpoint_version}/cars/{vin}/actions/{endpoint}."""
    car_adapter_url = get_car_adapter_url(root_url, account_id, endpoint_version, vin)
    url = f"{car_adapter_url}/actions/{endpoint}"
    headers = {
        "apikey": api_key,
        "x-gigya-id_token": gigya_jwt,
    }
    params = {"country": country}
    return cast(
        models.KamereonVehicleDataResponse,
        await request(
            websession,
            "POST",
            url,
            headers,
            params,
            data,
            schemas.KamereonVehicleDataResponseSchema,
        ),
    )


async def set_vehicle_hvac_start(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    attributes: Dict[str, Any],
) -> models.KamereonVehicleDataResponse:
    """POST to /cars/{vin}/actions/hvac-start."""
    data = {"type": "HvacStart", "attributes": attributes}
    return await set_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "hvac-start",
        data,
    )


async def set_vehicle_charge_schedule(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    attributes: Dict[str, Any],
) -> models.KamereonVehicleDataResponse:
    """POST to /cars/{vin}/actions/charge-schedule."""
    data = {"type": "ChargeSchedule", "attributes": attributes}
    return await set_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        2,
        vin,
        "charge-schedule",
        data,
    )


async def set_vehicle_charge_mode(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    attributes: Dict[str, Any],
) -> models.KamereonVehicleDataResponse:
    """POST to /cars/{vin}/actions/charge-mode."""
    data = {"type": "ChargeMode", "attributes": attributes}
    return await set_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "charge-mode",
        data,
    )


async def set_vehicle_charging_start(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    attributes: Dict[str, Any],
) -> models.KamereonVehicleDataResponse:
    """POST to /cars/{vin}/actions/charging-start."""
    data = {"type": "ChargingStart", "attributes": attributes}
    return await set_vehicle_data(
        websession,
        root_url,
        api_key,
        gigya_jwt,
        country,
        account_id,
        1,
        vin,
        "charging-start",
        data,
    )
