"""Kamereon models."""

import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any
from typing import cast
from warnings import warn

from marshmallow.schema import Schema

from . import enums
from . import exceptions
from . import helpers
from .enums import AssetPictureSize
from renault_api.models import BaseModel

_LOGGER = logging.getLogger(__name__)

COMMON_ERRRORS: list[dict[str, Any]] = [
    {
        "errorCode": "err.func.400",
        "error_type": exceptions.InvalidInputException,
    },
    {
        "errorCode": "err.func.403",
        "error_type": exceptions.AccessDeniedException,
    },
    {
        "errorCode": "err.tech.500",
        "error_type": exceptions.InvalidUpstreamException,
    },
    {
        "errorCode": "err.tech.501",
        "error_type": exceptions.NotSupportedException,
    },
    {
        "errorCode": "err.func.wired.notFound",
        "error_type": exceptions.ResourceNotFoundException,
    },
    {
        "errorCode": "err.tech.wired.kamereon-proxy",
        "error_type": exceptions.FailedForwardException,
    },
    {
        "errorCode": "err.func.wired.overloaded",
        "error_type": exceptions.QuotaLimitException,
    },
    {
        "errorCode": "err.func.wired.forbidden",
        "error_type": exceptions.ForbiddenException,
    },
]

VEHICLE_SPECIFICATIONS: dict[str, dict[str, Any]] = {
    "X101VE": {  # ZOE phase 1
        "reports-charge-session-durations-in-minutes": True,
        "reports-in-watts": True,
    },
    "XBG1VE": {  # DACIA SPRING
        "control-charge-via-kcm": True,
    },
}

GATEWAY_SPECIFICATIONS: dict[str, dict[str, Any]] = {
    "GDC": {  # ZOE phase 1
        "reports-charge-session-durations-in-minutes": True,
        "reports-in-watts": True,
    },
}


@dataclass
class EndpointDefinition:
    endpoint: str
    mode: str = "default"


_DEFAULT_ENDPOINTS: dict[str, EndpointDefinition] = {
    "actions/charge-set-mode": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/actions/charge-mode"
    ),
    "actions/charge-set-schedule": EndpointDefinition(
        "/kca/car-adapter/v2/cars/{vin}/actions/charge-schedule"
    ),
    "actions/charge-start": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/actions/charging-start"
    ),
    "actions/charge-stop": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/actions/charging-start"
    ),
    "actions/horn-start": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/actions/horn-lights"
    ),
    "actions/hvac-set-schedule": EndpointDefinition(
        "/kca/car-adapter/v2/cars/{vin}/actions/hvac-schedule"
    ),
    "actions/hvac-start": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/actions/hvac-start"
    ),
    "actions/hvac-stop": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/actions/hvac-start"
    ),
    "actions/lights-start": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/actions/horn-lights"
    ),
    "alerts": EndpointDefinition("/vehicles/{vin}/alerts"),
    "battery-status": EndpointDefinition(
        "/kca/car-adapter/v2/cars/{vin}/battery-status"
    ),
    "charge-history": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/charge-history"
    ),
    "charge-mode": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/charge-mode"),
    "charge-schedule": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/charge-schedule"
    ),
    "charges": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/charges"),
    "charging-settings": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/charging-settings"
    ),
    "cockpit": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/cockpit"),
    "hvac-history": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/hvac-history"),
    "hvac-sessions": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/hvac-sessions"),
    "hvac-settings": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/hvac-settings"),
    "hvac-status": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/hvac-status"),
    "location": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/location"),
    "lock-status": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/lock-status"),
    "notification-settings": EndpointDefinition(
        "/kca/car-adapter/v1/cars/{vin}/notification-settings"
    ),
    "pressure": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/pressure"),
    "res-state": EndpointDefinition("/kca/car-adapter/v1/cars/{vin}/res-state"),
    "soc-levels": EndpointDefinition("/kcm/v1/vehicles/{vin}/ev/soc-levels"),
}
_KCM_ENDPOINTS: dict[str, EndpointDefinition] = {
    "actions/charge-start": EndpointDefinition(
        "/kcm/v1/vehicles/{vin}/charge/pause-resume", mode="kcm"
    ),
    "actions/charge-stop": EndpointDefinition(
        "/kcm/v1/vehicles/{vin}/charge/pause-resume", mode="kcm"
    ),
    "charge-schedule": EndpointDefinition(
        "/kcm/v1/vehicles/{vin}/ev/settings", mode="kcm"
    ),
}

_VEHICLE_ENDPOINTS: dict[str, dict[str, EndpointDefinition | None]] = {
    "R5E1VE": {  # Renault 5 E-TECH
        "actions/horn-start": _DEFAULT_ENDPOINTS["actions/horn-start"],
        "actions/hvac-start": _DEFAULT_ENDPOINTS["actions/hvac-start"],
        "actions/lights-start": _DEFAULT_ENDPOINTS["actions/lights-start"],
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-history": None,  # Reason: "you should not be there..."
        "charge-mode": None,  # Reason: The access is forbidden
        "charge-schedule": _KCM_ENDPOINTS["charge-schedule"],
        "charges": _DEFAULT_ENDPOINTS["charges"],
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-settings": _DEFAULT_ENDPOINTS["hvac-settings"],
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,  # Reason: 404
        "pressure": None,  # Reason: 404
        "res-state": None,  # Reason: The access is forbidden
        "soc-levels": _DEFAULT_ENDPOINTS["soc-levels"],
    },
    "X071VE": {  # TWINGO III
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-history": None,  # Reason: "err.func.wired.not-found"
        "charge-mode": None,  # Reason: "err.func.vcps.ev.charge-mode.error"
        "charge-schedule": None,  # Reason: "err.func.vcps.ev.charge-schedule.error"
        "charging-settings": _DEFAULT_ENDPOINTS["charging-settings"],
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-history": None,  # Reason: "err.func.wired.not-found"
        "hvac-sessions": None,  # Reason: "err.func.wired.not-found"
        "hvac-settings": _DEFAULT_ENDPOINTS["hvac-settings"],
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,  # Reason: "err.func.wired.notFound"
        "notification-settings": None,  # Reason: "err.func.vcps.users-helper.get-notification-settings.error"  # noqa: E501
        "pressure": None,  # Reason: "err.func.wired.notFound"
        "res-state": None,  # Reason: "err.func.wired.notFound"
    },
    "X101VE": {  # ZOE phase 1
        "actions/hvac-start": _DEFAULT_ENDPOINTS["actions/hvac-start"],
        "actions/hvac-stop": _DEFAULT_ENDPOINTS["actions/hvac-stop"],
        "actions/charge-start": _DEFAULT_ENDPOINTS["actions/charge-start"],
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],  # confirmed
        "charge-mode": _DEFAULT_ENDPOINTS["charge-mode"],  # confirmed
        "charge-schedule": _DEFAULT_ENDPOINTS["charge-schedule"],  # confirmed
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],  # confirmed
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],  # confirmed
        "location": None,  # not supported
        "lock-status": None,  # not supported
        "pressure": None,  # not supported
        "res-state": None,  # not supported
        "soc-levels": None,  # not supported
    },
    "X102VE": {  # ZOE phase 2
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-mode": None,  # default => 400 Bad Request
        "charge-schedule": None,  # default and _KCM_ENDPOINTS["charge-schedule"] => 404
        "charging-settings": _DEFAULT_ENDPOINTS["charging-settings"],
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-settings": _DEFAULT_ENDPOINTS["hvac-settings"],
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,  # default => 404
        # pressure not supported by all vehicles - but confirmed to be working on some
        "pressure": _DEFAULT_ENDPOINTS["pressure"],
        "res-state": None,  # default => 404
    },
    "XBG1VE": {  # DACIA SPRING
        "actions/charge-start": _KCM_ENDPOINTS["actions/charge-start"],
        "actions/charge-stop": _KCM_ENDPOINTS["actions/charge-stop"],
        "alerts": None,  # Reason: "err.func.wired.not-found"
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-history": None,  # Reason: "err.func.wired.not-found"
        "charge-mode": None,  # Reason: "err.func.wired.forbidden"
        "charge-schedule": None,  # Reason: "err.func.wired.forbidden"
        "charging-settings": None,  # Reason: "err.func.wired.forbidden"
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-history": None,  # Reason: "err.func.wired.not-found"
        "hvac-sessions": None,  # Reason: "err.func.wired.not-found"
        "hvac-settings": None,  # Reason: "err.tech.vcps.ev.hvac-settings.error"
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,  # Reason: "err.func.wired.notFound"
        "notification-settings": None,  # Reason: "err.func.vcps.users-helper.get-notification-settings.error"  # noqa: E501
        "pressure": None,  # Reason: "err.func.wired.notFound"
        "res-state": None,  # Reason: "err.func.wired.notFound"
        "soc-levels": None,  # Reason: "err.func.wired.forbidden"
    },
    "XCB1SE": {  # SCENIC E-TECH
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-mode": None,
        "charge-schedule": _KCM_ENDPOINTS["charge-schedule"],
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-settings": _DEFAULT_ENDPOINTS["hvac-settings"],
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,
        "res-state": None,
    },
    "XCB1VE": {  # MEGANE E-TECH
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-history": None,  # Reason: "err.func.wired.not-found"
        "charge-mode": None,  # Reason: "err.func.vcps.ev.charge-mode.error"
        "charge-schedule": None,  # Reason: "err.func.vcps.ev.charge-schedule.error"
        "charging-settings": _DEFAULT_ENDPOINTS["charging-settings"],
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-history": None,  # Reason: "err.func.wired.not-found"
        "hvac-sessions": None,  # Reason: "err.func.wired.not-found"
        "hvac-settings": _DEFAULT_ENDPOINTS["hvac-settings"],
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,  # Reason: "err.func.wired.notFound"
        "notification-settings": None,  # Reason: "err.func.vcps.users-helper.get-notification-settings.error"  # noqa: E501
        "pressure": None,  # Reason: "err.func.wired.notFound"
        "res-state": None,  # Reason: "err.func.wired.notFound"
    },
    "XFB2BI": {  # Megane IV
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-history": None,  # Reason: "err.func.wired.not-found"
        "charge-mode": None,  # Reason: "err.func.vcps.ev.charge-mode.error"
        "charge-schedule": None,  # Reason: "err.func.vcps.ev.charge-schedule.error"
        "charging-settings": _DEFAULT_ENDPOINTS["charging-settings"],
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-history": None,  # Reason: "err.func.wired.not-found"
        "hvac-sessions": None,  # Reason: "err.func.wired.not-found"
        "hvac-settings": _DEFAULT_ENDPOINTS["hvac-settings"],
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": None,  # Reason: "err.func.wired.notFound"
        "lock-status": None,  # Reason: "err.func.wired.notFound"
        "notification-settings": None,  # Reason: "err.func.vcps.users-helper.get-notification-settings.error"  # noqa: E501
        "pressure": None,  # Reason: "err.func.wired.notFound"
        "res-state": None,  # Reason: "err.func.wired.notFound"
    },
    "XHN1SU": {  # AUSTRAL
        "actions/horn-start": _DEFAULT_ENDPOINTS["actions/horn-start"],
        "actions/lights-start": _DEFAULT_ENDPOINTS["actions/lights-start"],
        "battery-status": None,  # Reason: "err.func.wired.notFound"
        "charge-history": None,  # Reason: "err.func.wired.not-found"
        "charge-mode": None,  # Reason: "err.func.wired.forbidden"
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],  # confirmed
        "hvac-status": None,
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,
        "pressure": None,  # Reason: 404
        "res-state": None,
    },
    "XHN1ML": {  # Renault Espace VI (OpenRLink)
        "actions/hvac-start": None,  # err.func.wired.forbidden
        "actions/horn-start": _DEFAULT_ENDPOINTS["actions/horn-start"],
        "actions/lights-start": _DEFAULT_ENDPOINTS["actions/lights-start"],
        "battery-status": None,  # err.func.wired.notFound
        "charge-history": None,  # err.func.wired.not-found
        "charge-mode": None,  # err.func.wired.forbidden
        "charge-schedule": None,  # err.func.wired.forbidden
        "charges": None,  # err.func.wired.forbidden
        "charging-settings": None,  # err.func.wired.forbidden
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-history": None,  # err.func.wired.not-found
        "hvac-sessions": None,  # err.func.wired.not-found
        "hvac-settings": None,  # err.func.wired.forbidden
        "hvac-status": None,  # err.func.wired.notFound
        "location": _DEFAULT_ENDPOINTS["location"],
        "notification-settings": None,  # err.func.vcps.users-helper.get-notification-settings.error  # noqa: E501
        "lock-status": None,  # err.func.wired.notFound
        "pressure": None,  # err.func.wired.notFound
        "res-state": None,  # err.func.wired.notFound
        "soc-levels": None,  # err.func.wired.notFound
    },
    "XJA1VP": {  # CLIO V
        "hvac-status": None,
    },
    "XJB2CP": {  # Renault Symbioz 2025
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],  # confirmed
        "hvac-status": None,
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,
        "res-state": None,
    },
    "XJB1SU": {  # CAPTUR II
        "battery-status": _DEFAULT_ENDPOINTS["battery-status"],
        "charge-history": None,  # Reason: "err.func.wired.not-found"
        "charge-mode": None,  # Reason: "err.func.vcps.ev.charge-mode.error"
        "charge-schedule": None,  # Reason: "err.func.vcps.ev.charge-schedule.error"
        "charging-settings": _DEFAULT_ENDPOINTS["charging-settings"],
        "cockpit": _DEFAULT_ENDPOINTS["cockpit"],
        "hvac-history": None,  # Reason: "err.func.wired.not-found"
        "hvac-sessions": None,  # Reason: "err.func.wired.not-found"
        "hvac-settings": _DEFAULT_ENDPOINTS["hvac-settings"],
        "hvac-status": _DEFAULT_ENDPOINTS["hvac-status"],
        "location": _DEFAULT_ENDPOINTS["location"],
        "lock-status": None,  # Reason: "err.func.wired.notFound"
        "notification-settings": None,  # Reason: "err.func.vcps.users-helper.get-notification-settings.error"  # noqa: E501
        "pressure": None,  # Reason: "err.func.wired.notFound"
        "res-state": None,  # Reason: "err.func.wired.notFound"
    },
}

_ALREADY_WARNED_VEHICLE: set[str] = set()
_ALREADY_WARNED_VEHICLE_ENDPOINT: set[str] = set()


def get_model_endpoints(
    model_code: str | None,
) -> Mapping[str, EndpointDefinition | None]:
    """Return model endpoints."""
    if not model_code:
        # Model code not available
        return _DEFAULT_ENDPOINTS

    if model_code not in _VEHICLE_ENDPOINTS:
        # Model not documented
        if model_code not in _ALREADY_WARNED_VEHICLE:
            _ALREADY_WARNED_VEHICLE.add(model_code)
            _LOGGER.warning(
                "Model %s is not documented, using default endpoints."
                " Please help to document it at https://github.com/hacf-fr/renault-api",
                model_code,
            )
        return _DEFAULT_ENDPOINTS

    return _VEHICLE_ENDPOINTS[model_code]


def get_model_endpoint(
    model_code: str | None, endpoint: str
) -> EndpointDefinition | None:
    """Return model endpoint"""
    endpoints = get_model_endpoints(model_code)

    if endpoint not in endpoints:
        # Endpoint not documented
        key = f"{model_code}:{endpoint}"
        if key not in _ALREADY_WARNED_VEHICLE_ENDPOINT:
            _ALREADY_WARNED_VEHICLE_ENDPOINT.add(key)
            _LOGGER.warning(
                "Endpoint %s for model %s is not documented, using default endpoints."
                " Please help to document it at https://github.com/hacf-fr/renault-api",
                endpoint,
                model_code,
            )
        return _DEFAULT_ENDPOINTS.get(endpoint)

    return endpoints[endpoint]


@dataclass
class KamereonResponseError(BaseModel):
    """Kamereon response error."""

    errorCode: str | None
    errorMessage: str | None

    def raise_for_error_code(self) -> None:
        """Raise exception from response error."""
        error_details = self.get_error_details()
        for common_error in COMMON_ERRRORS:
            if self.errorCode == common_error["errorCode"]:
                error_type = common_error["error_type"]
                raise error_type(self.errorCode, error_details)
        raise exceptions.KamereonResponseException(self.errorCode, error_details)

    def get_error_details(self) -> str | None:
        """Extract the error details sometimes hidden inside nested JSON."""
        try:
            error_details = json.loads(self.errorMessage or "{}")
        except json.JSONDecodeError:
            return self.errorMessage

        error_descriptions = []
        for inner_error in error_details.get("errors", []):
            error_description = " ".join(
                filter(
                    None,
                    [
                        inner_error.get("title"),
                        inner_error.get("source", {}).get("pointer"),
                        inner_error.get("detail"),
                    ],
                )
            )
            error_descriptions.append(error_description)

        return ", ".join(error_descriptions) or self.errorMessage


@dataclass
class KamereonResponse(BaseModel):
    """Kamereon response."""

    errors: list[KamereonResponseError] | None

    def raise_for_error_code(self) -> None:
        """Raise exception if errors found in the response."""
        for error in self.errors or []:
            # Until we have a sample for multiple errors, just raise on first one
            error.raise_for_error_code()


@dataclass
class KamereonPersonAccount(BaseModel):
    """Kamereon person account data."""

    accountId: str | None
    accountType: str | None
    accountStatus: str | None


@dataclass
class KamereonPersonResponse(KamereonResponse):
    """Kamereon response to GET on /persons/{gigya_person_id}."""

    accounts: list[KamereonPersonAccount] | None


@dataclass
class KamereonVehicleDetailsGroup(BaseModel):
    """Kamereon vehicle details group data."""

    code: str | None
    label: str | None
    group: str | None


@dataclass
class KamereonVehicleDetails(BaseModel):
    """Kamereon vehicle details."""

    vin: str | None
    registrationNumber: str | None
    radioCode: str | None
    brand: KamereonVehicleDetailsGroup | None
    model: KamereonVehicleDetailsGroup | None
    energy: KamereonVehicleDetailsGroup | None
    engineEnergyType: str | None
    assets: list[dict[str, Any]] | None

    def get_energy_code(self) -> str | None:
        """Return vehicle energy code."""
        return self.energy.code if self.energy else None

    def get_brand_label(self) -> str | None:
        """Return vehicle model label."""
        return self.brand.label if self.brand else None

    def get_model_code(self) -> str | None:
        """Return vehicle model code."""
        return self.model.code if self.model else None

    def get_model_label(self) -> str | None:
        """Return vehicle model label."""
        return self.model.label if self.model else None

    def get_asset(self, asset_type: str) -> dict[str, Any] | None:
        """Return asset."""
        return next(
            filter(
                lambda asset: asset.get("assetType") == asset_type, self.assets or []
            )
        )

    def get_picture(
        self, size: AssetPictureSize = AssetPictureSize.LARGE
    ) -> str | None:
        """Return vehicle picture."""
        asset: dict[str, Any] = self.get_asset("PICTURE") or {}

        rendition: dict[str, str] = next(
            filter(
                lambda rendition: rendition.get("resolutionType")
                == f"ONE_MYRENAULT_{size.name}",
                asset.get("renditions", [{}]),
            )
        )

        return rendition.get("url") if rendition else None

    def uses_electricity(self) -> bool:
        """Return True if model uses electricity."""
        energy_type = self.engineEnergyType or self.get_energy_code()
        if energy_type in [
            "ELEC",
            "ELECX",
            "PHEV",
        ]:
            return True
        return False

    def uses_fuel(self) -> bool:
        """Return True if model uses fuel."""
        energy_type = self.engineEnergyType or self.get_energy_code()
        if energy_type in [
            "OTHER",
            "PHEV",
            "HEV",
        ]:
            return True
        return False

    def reports_charge_session_durations_in_minutes(self) -> bool:
        """Return True if model reports history durations in minutes."""
        # Default to False (=seconds) for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.model.code, {}
            ).get("reports-charge-session-durations-in-minutes", False)
        return False

    def reports_charging_power_in_watts(self) -> bool:
        """Return True if model reports chargingInstantaneousPower in watts."""
        # Default to False for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.model.code, {}
            ).get("reports-in-watts", False)
        return False

    def supports_endpoint(self, endpoint: str) -> bool:
        """Return True if model supports specified endpoint."""
        # Default to True for unknown vehicles
        return self.get_endpoint(endpoint) is not None

    def controls_action_via_kcm(self, action: str) -> bool:
        """Return True if model uses endpoint via kcm."""
        warn(  # Deprecated in v0.3.2
            "This method is deprecated, please use get_endpoint.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Default to False for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.model.code, {}
            ).get(f"control-{action}-via-kcm", False)
        return False

    def get_endpoints(self) -> Mapping[str, EndpointDefinition | None]:
        """Return model endpoints."""
        return get_model_endpoints(self.get_model_code())

    def get_endpoint(self, endpoint: str) -> EndpointDefinition | None:
        """Return model endpoint"""
        return get_model_endpoint(self.get_model_code(), endpoint)


@dataclass
class KamereonVehiclesLink(BaseModel):
    """Kamereon vehicles link data."""

    vin: str | None
    vehicleDetails: KamereonVehicleDetails | None


@dataclass
class KamereonVehiclesResponse(KamereonResponse):
    """Kamereon response to GET on /accounts/{account_id}/vehicles."""

    accountId: str | None
    country: str | None
    vehicleLinks: list[KamereonVehiclesLink] | None


@dataclass
class KamereonVehicleDetailsResponse(KamereonResponse, KamereonVehicleDetails):
    """Kamereon response to GET on /accounts/{account_id}/vehicles/{vin}/details."""


@dataclass
class KamereonVehicleDataAttributes(BaseModel):
    """Kamereon vehicle data attributes."""


@dataclass
class KamereonVehicleContract(BaseModel):
    """Kamereon vehicle contract."""

    type: str | None
    contractId: str | None
    code: str | None
    group: str | None
    durationMonths: int | None
    startDate: str | None
    endDate: str | None
    status: str | None
    statusLabel: str | None
    description: str | None


@dataclass
class KamereonVehicleContractsResponse(KamereonResponse):
    """Kamereon response to GET on /accounts/{accountId}/vehicles/{vin}/contracts."""

    contractList: list[KamereonVehicleContract] | None


@dataclass
class KamereonVehicleData(BaseModel):
    """Kamereon vehicle data."""

    type: str | None
    id: str | None
    attributes: dict[str, Any] | None


@dataclass
class KamereonVehicleDataResponse(KamereonResponse):
    """Kamereon response to GET/POST on .../cars/{vin}/{type}."""

    data: KamereonVehicleData | None

    def get_attributes(self, schema: Schema) -> KamereonVehicleDataAttributes:
        """Return jwt token."""
        attributes = {}
        if self.data and self.data.attributes is not None:
            attributes = self.data.attributes
        return cast(KamereonVehicleDataAttributes, schema.load(attributes))


@dataclass
class KamereonVehicleBatteryStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle battery-status data."""

    timestamp: str | None
    batteryLevel: int | None
    batteryTemperature: int | None
    batteryAutonomy: int | None
    batteryCapacity: int | None
    batteryAvailableEnergy: int | None
    plugStatus: int | None
    chargingStatus: float | None
    chargingRemainingTime: int | None
    chargingInstantaneousPower: float | None

    def get_plug_status(self) -> enums.PlugState | None:
        """Return plug status."""
        try:
            return (
                enums.PlugState(self.plugStatus)
                if self.plugStatus is not None
                else None
            )
        except ValueError:
            _LOGGER.warning("Unable to convert `%s` to PlugState.", self.plugStatus)
            return None

    def get_charging_status(self) -> enums.ChargeState | None:
        """Return charging status."""
        try:
            return (
                enums.ChargeState(self.chargingStatus)
                if self.chargingStatus is not None
                else None
            )
        except ValueError:
            _LOGGER.warning(
                "Unable to convert `%s` to ChargeState.", self.chargingStatus
            )
            return None


@dataclass
class KamereonVehicleBatterySocData(KamereonVehicleDataAttributes):
    """Kamereon vehicle battery state of charge limits data."""

    lastEnergyUpdateTimestamp: str | None
    socMin: int | None
    socTarget: int | None


@dataclass
class KamereonVehicleTyrePressureData(KamereonVehicleDataAttributes):
    """Kamereon vehicle tyre-pressure data."""

    flPressure: int | None
    frPressure: int | None
    rlPressure: int | None
    rrPressure: int | None
    flStatus: int | None
    frStatus: int | None
    rlStatus: int | None
    rrStatus: int | None


@dataclass
class KamereonVehicleLocationData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data location attributes."""

    lastUpdateTime: str | None
    gpsLatitude: float | None
    gpsLongitude: float | None


@dataclass
class KamereonVehicleHvacStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-status attributes."""

    lastUpdateTime: str | None
    externalTemperature: float | None
    hvacStatus: str | None
    nextHvacStartDate: str | None
    socThreshold: float | None


@dataclass
class KamereonVehicleChargeModeData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charge-mode attributes."""

    chargeMode: str | None


@dataclass
class KamereonVehicleCockpitData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data cockpit attributes."""

    fuelAutonomy: float | None
    fuelQuantity: float | None
    totalMileage: float | None


@dataclass
class KamereonVehicleLockStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data lock-status attributes."""

    lockStatus: str | None
    doorStatusRearLeft: str | None
    doorStatusRearRight: str | None
    doorStatusDriver: str | None
    doorStatusPassenger: str | None
    hatchStatus: str | None
    lastUpdateTime: str | None


@dataclass
class KamereonVehicleResStateData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data res-set attributes."""

    details: str | None
    code: str | None


@dataclass
class KamereonVehicleCarAdapterData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-status attributes."""

    vin: str | None
    vehicleId: int | None
    batteryCode: str | None
    brand: str | None
    canGeneration: str | None
    carGateway: str | None
    deliveryCountry: str | None
    deliveryDate: str | None
    energy: str | None
    engineType: str | None
    familyCode: str | None
    firstRegistrationDate: str | None
    gearbox: str | None
    modelCode: str | None
    modelCodeDetail: str | None
    modelName: str | None
    radioType: str | None
    region: str | None
    registrationCountry: str | None
    registrationNumber: str | None
    tcuCode: str | None
    versionCode: str | None
    privacyMode: str | None
    privacyModeUpdateDate: str | None
    svtFlag: bool | None
    svtBlockFlag: bool | None

    def uses_electricity(self) -> bool:
        """Return True if model uses electricity."""
        if self.energy in [
            "electric",
        ]:
            return True
        return False

    def uses_fuel(self) -> bool:
        """Return True if model uses fuel."""
        if self.energy in [
            "gasoline",
        ]:
            return True
        return False

    def reports_charging_power_in_watts(self) -> bool:
        """Return True if model reports chargingInstantaneousPower in watts."""
        # Default to False for unknown vehicles
        if self.carGateway:
            return GATEWAY_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.carGateway, {}
            ).get("reports-in-watts", False)
        return False

    def controls_action_via_kcm(self, action: str) -> bool:
        """Return True if model uses endpoint via kcm."""
        warn(  # Deprecated in v0.3.2
            "This method is deprecated, please use get_endpoint.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Default to False for unknown vehicles
        if self.modelCodeDetail:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.modelCodeDetail, {}
            ).get(f"control-{action}-via-kcm", False)
        return False


@dataclass
class ChargeDaySchedule(BaseModel):
    """Kamereon vehicle charge schedule for day."""

    startTime: str | None
    duration: int | None

    def for_json(self) -> dict[str, Any]:
        """Create dict for json."""
        return {
            "startTime": self.startTime,
            "duration": self.duration,
        }

    def get_end_time(self) -> str | None:
        """Get end time."""
        if self.startTime is None:
            return None
        return helpers.get_end_time(self.startTime, self.duration)


@dataclass
class ChargeSchedule(BaseModel):
    """Kamereon vehicle charge schedule for week."""

    id: int | None
    activated: bool | None
    monday: ChargeDaySchedule | None
    tuesday: ChargeDaySchedule | None
    wednesday: ChargeDaySchedule | None
    thursday: ChargeDaySchedule | None
    friday: ChargeDaySchedule | None
    saturday: ChargeDaySchedule | None
    sunday: ChargeDaySchedule | None

    def for_json(self) -> dict[str, Any]:
        """Create dict for json."""
        result: dict[str, Any] = {
            "id": self.id,
            "activated": self.activated,
        }
        for day in helpers.DAYS_OF_WEEK:
            day_spec: ChargeDaySchedule | None = getattr(self, day, None)
            if day_spec is None:
                result[day] = day_spec
            else:
                result[day] = day_spec.for_json()
        return result


@dataclass
class HvacDaySchedule(BaseModel):
    """Kamereon vehicle hvac schedule for day."""

    readyAtTime: str | None

    def for_json(self) -> dict[str, str | None]:
        """Create dict for json."""
        return {
            "readyAtTime": self.readyAtTime,
        }


@dataclass
class HvacSchedule(BaseModel):
    """Kamereon vehicle hvac schedule for week."""

    id: int | None
    activated: bool | None
    monday: HvacDaySchedule | None
    tuesday: HvacDaySchedule | None
    wednesday: HvacDaySchedule | None
    thursday: HvacDaySchedule | None
    friday: HvacDaySchedule | None
    saturday: HvacDaySchedule | None
    sunday: HvacDaySchedule | None

    def for_json(self) -> dict[str, Any]:
        """Create dict for json."""
        result: dict[str, Any] = {
            "id": self.id,
            "activated": self.activated,
        }
        for day in helpers.DAYS_OF_WEEK:
            day_spec: HvacDaySchedule | None = getattr(self, day, None)
            if day_spec is None:
                result[day] = day_spec
            else:
                result[day] = day_spec.for_json()
        return result


@dataclass
class KamereonVehicleChargingSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charging-settings attributes."""

    mode: str | None
    schedules: list[ChargeSchedule] | None

    def update(self, args: dict[str, Any]) -> None:
        """Update schedule."""
        if "id" not in args:
            raise ValueError("id not provided for update.")
        if self.schedules is None:
            self.schedules = []
        for schedule in self.schedules:
            if schedule.id == args["id"]:
                helpers.update_charge_schedule(schedule, args)
                return
        self.schedules.append(helpers.create_charge_schedule(args))


@dataclass
class KamereonVehicleHvacSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-settings (mode+schedules) attributes."""

    mode: str | None
    schedules: list[HvacSchedule] | None

    def update(self, args: dict[str, Any]) -> None:
        """Update schedule."""
        if "id" not in args:
            raise ValueError("id not provided for update.")
        if self.schedules is None:
            self.schedules = []
        for schedule in self.schedules:
            if schedule.id == args["id"]:
                helpers.update_hvac_schedule(schedule, args)
                return
        self.schedules.append(helpers.create_hvac_schedule(args))


@dataclass
class KamereonVehicleNotificationSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data notification-settings attributes."""


@dataclass
class KamereonVehicleChargeHistoryData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charge-history attributes."""


@dataclass
class KamereonVehicleChargesData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charges attributes."""


@dataclass
class KamereonVehicleHvacHistoryData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-history attributes."""


@dataclass
class KamereonVehicleHvacSessionsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-sessions attributes."""


@dataclass
class KamereonVehicleHvacStartActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data hvac-start attributes."""


@dataclass
class KamereonVehicleHvacScheduleActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data hvac-schedule attributes."""


@dataclass
class KamereonVehicleChargeScheduleActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charge-schedule attributes."""


@dataclass
class KamereonVehicleChargeModeActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charge-mode attributes."""


@dataclass
class KamereonVehicleHvacModeActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data hvac-mode attributes."""


@dataclass
class KamereonVehicleChargingStartActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charging-start attributes."""
