"""Kamereon API."""
import logging
from json import dumps as json_dumps
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from warnings import warn

import aiohttp
from marshmallow.schema import Schema

from . import models
from . import schemas
from .exceptions import KamereonResponseException


_LOGGER = logging.getLogger(__name__)


_KCA_GET_ENDPOINTS: Dict[str, Any] = {
    "": {"version": 2},
    "battery-status": {"version": 2},
    "charge-history": {"version": 1},
    "charge-mode": {"version": 1},
    "charges": {"version": 1},
    "charging-settings": {"version": 1},
    "cockpit": {"version": 2},
    "hvac-history": {"version": 1},
    "hvac-sessions": {"version": 1},
    "hvac-status": {"version": 1},
    "hvac-settings": {"version": 1},
    "location": {"version": 1},
    "lock-status": {"version": 1},
    "notification-settings": {"version": 1},
    "res-state": {"version": 1},
}
_KCA_POST_ENDPOINTS: Dict[str, Any] = {
    "actions/charge-mode": {"version": 1, "type": "ChargeMode"},
    "actions/charge-schedule": {"version": 2, "type": "ChargeSchedule"},
    "actions/charging-start": {"version": 1, "type": "ChargingStart"},
    "actions/hvac-schedule": {"version": 2, "type": "HvacSchedule"},
    "actions/hvac-start": {"version": 1, "type": "HvacStart"},
}
_KCM_POST_ENDPOINTS: Dict[str, Any] = {
    "charge/pause-resume": {"version": 1, "type": "ChargePauseResume"},
}

# Deprecated from 0.1.8 - kept for compatibility
DATA_ENDPOINTS = _KCA_GET_ENDPOINTS
ACTION_ENDPOINTS = _KCA_POST_ENDPOINTS


def get_commerce_url(root_url: str) -> str:
    """Get the Kamereon base commerce url."""
    return f"{root_url}/commerce/v1"


def get_person_url(root_url: str, person_id: str) -> str:
    """Get the url to the person."""
    return f"{get_commerce_url(root_url)}/persons/{person_id}"


def get_account_url(root_url: str, account_id: str) -> str:
    """Get the url to the account."""
    return f"{get_commerce_url(root_url)}/accounts/{account_id}"


def get_car_adapter_url(
    root_url: str, account_id: str, version: int, vin: str, *, adapter_type: str = "kca"
) -> str:
    """Get the url to the car adapter."""
    account_url = get_account_url(root_url, account_id)
    if adapter_type == "kcm":
        return f"{account_url}/kamereon/kcm/v{version}/vehicles/{vin}"
    return f"{account_url}/kamereon/kca/car-adapter/v{version}/cars/{vin}"


def get_contracts_url(root_url: str, account_id: str, vin: str) -> str:
    """Get the url to the car contracts."""
    account_url = get_account_url(root_url, account_id)
    return f"{account_url}/vehicles/{vin}/contracts"


def get_required_contracts(endpoint: str) -> str:  # pragma: no cover
    """Get the required contracts for the specified endpoint."""
    # "Deprecated in 0.1.3, contract codes are country-specific"
    # " and can't be used to guess requirements."
    warn("This method is deprecated.", DeprecationWarning, stacklevel=2)
    return ""


def has_required_contracts(
    contracts: List[models.KamereonVehicleContract], endpoint: str
) -> bool:
    """Check if vehicle has contract for endpoint."""
    # "Deprecated in 0.1.3, contract codes are country-specific"
    # " and can't be used to guess requirements."
    warn("This method is deprecated.", DeprecationWarning, stacklevel=2)
    return True  # pragma: no cover


async def request(
    websession: aiohttp.ClientSession,
    method: str,
    url: str,
    api_key: str,
    gigya_jwt: str,
    params: Dict[str, str],
    json: Optional[Dict[str, Any]] = None,
    schema: Optional[Schema] = None,
    *,
    wrap_array_in: Optional[str] = None,
) -> models.KamereonResponse:
    """Process Kamereon HTTP request."""
    schema = schema or schemas.KamereonResponseSchema
    headers = {
        "Content-type": "application/vnd.api+json",
        "apikey": api_key,
        "x-gigya-id_token": gigya_jwt,
    }
    async with websession.request(
        method,
        url,
        headers=headers,
        params=params,
        json=json,
    ) as http_response:
        response_text = await http_response.text()
        if json:
            _LOGGER.debug(
                "Send Kamereon %s request to %s with body: %s",
                method,
                http_response.url,
                json_dumps(json),
            )
        _LOGGER.debug(
            "Received Kamereon response %s on %s to %s: %s",
            http_response.status,
            method,
            http_response.url,
            response_text,
        )

        # Some endpoints return arrays instead of objects.
        # These need to be wrapped in an object.
        if response_text.startswith("["):
            response_text = f'{{"{wrap_array_in or "data"}": {response_text}}}'
        if not response_text.startswith("{"):
            # Check for HTTP error
            http_response.raise_for_status()
            raise KamereonResponseException("Invalid JSON", response_text)

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
    params = {"country": country}
    return cast(
        models.KamereonPersonResponse,
        await request(
            websession,
            "GET",
            url,
            api_key,
            gigya_jwt,
            params=params,
            schema=schemas.KamereonPersonResponseSchema,
        ),
    )


async def get_vehicle_contracts(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    locale: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleContractsResponse:
    """GET to /accounts/{accountId}/vehicles/{vin}/contracts."""
    url = get_contracts_url(root_url, account_id, vin)
    params = {
        "country": country,
        "locale": locale,
        "brand": "RENAULT",
        "connectedServicesContracts": "true",
        "warranty": "true",
        "warrantyMaintenanceContracts": "true",
    }

    return cast(
        models.KamereonVehicleContractsResponse,
        await request(
            websession,
            "GET",
            url,
            api_key,
            gigya_jwt,
            params=params,
            schema=schemas.KamereonVehicleContractsResponseSchema,
            wrap_array_in="contractList",
        ),
    )


async def get_account_vehicles(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
) -> models.KamereonVehiclesResponse:
    """GET to /accounts/{account_id}/vehicles."""
    url = f"{get_account_url(root_url, account_id)}/vehicles"
    params = {"country": country}
    return cast(
        models.KamereonVehiclesResponse,
        await request(
            websession,
            "GET",
            url,
            api_key,
            gigya_jwt,
            params=params,
            schema=schemas.KamereonVehiclesResponseSchema,
        ),
    )


async def get_vehicle_details(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
) -> models.KamereonVehicleDetailsResponse:
    """GET to /accounts/{account_id}/vehicles/{vin}/details."""
    url = f"{get_account_url(root_url, account_id)}/vehicles/{vin}/details"
    params = {"country": country}
    return cast(
        models.KamereonVehicleDetailsResponse,
        await request(
            websession,
            "GET",
            url,
            api_key,
            gigya_jwt,
            params=params,
            schema=schemas.KamereonVehicleDetailsResponseSchema,
        ),
    )


async def get_vehicle_data(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    endpoint: str,
    endpoint_version: Optional[int] = None,
    params: Optional[Dict[str, str]] = None,
    *,
    adapter_type: str = "kca",
) -> models.KamereonVehicleDataResponse:
    """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
    endpoint_details = _KCA_GET_ENDPOINTS[endpoint]
    car_adapter_url = get_car_adapter_url(
        root_url=root_url,
        account_id=account_id,
        version=endpoint_version or int(endpoint_details["version"]),
        vin=vin,
        adapter_type=adapter_type,
    )
    url = f"{car_adapter_url}/{endpoint}" if endpoint else car_adapter_url
    params = params or {}
    params["country"] = country
    return cast(
        models.KamereonVehicleDataResponse,
        await request(
            websession,
            "GET",
            url,
            api_key,
            gigya_jwt,
            params=params,
            schema=schemas.KamereonVehicleDataResponseSchema,
        ),
    )


async def set_vehicle_action(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_jwt: str,
    country: str,
    account_id: str,
    vin: str,
    endpoint: str,
    attributes: Dict[str, Any],
    endpoint_version: Optional[int] = None,
    data_type: Optional[Dict[str, Any]] = None,
    *,
    adapter_type: str = "kca",
) -> models.KamereonVehicleDataResponse:
    """POST to /v{endpoint_version}/cars/{vin}/{endpoint}."""
    if "/" not in endpoint:
        # Deprecated in 0.1.8
        warn(
            f"You should use the full endpoint: actions/{endpoint}.",
            DeprecationWarning,
            stacklevel=2,
        )
        endpoint = f"actions/{endpoint}"

    if adapter_type == "kcm":
        endpoint_details = _KCM_POST_ENDPOINTS[endpoint]
    else:
        endpoint_details = _KCA_POST_ENDPOINTS[endpoint]
    car_adapter_url = get_car_adapter_url(
        root_url=root_url,
        account_id=account_id,
        version=endpoint_version or int(endpoint_details["version"]),
        vin=vin,
        adapter_type=adapter_type,
    )

    url = f"{car_adapter_url}/{endpoint}"
    params = {"country": country}
    json = {
        "data": {
            "type": data_type or endpoint_details["type"],
            "attributes": attributes,
        }
    }
    return cast(
        models.KamereonVehicleDataResponse,
        await request(
            websession,
            "POST",
            url,
            api_key,
            gigya_jwt,
            params,
            json,
            schemas.KamereonVehicleDataResponseSchema,
        ),
    )
