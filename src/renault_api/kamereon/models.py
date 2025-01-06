"""Kamereon models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from typing import cast

from marshmallow.schema import Schema

from . import enums
from . import exceptions
from . import helpers
from .enums import AssetPictureSize
from renault_api.models import BaseModel

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
]

VEHICLE_SPECIFICATIONS: dict[str, dict[str, Any]] = {
    "X101VE": {  # ZOE phase 1
        "reports-charge-session-durations-in-minutes": True,
        "reports-in-watts": True,
        "support-endpoint-location": False,
        "support-endpoint-lock-status": False,
    },
    "X102VE": {  # ZOE phase 2
        "warns-on-method-set_ac_stop": "Action `cancel` on endpoint `hvac-start` may not be supported on this model.",  # noqa
    },
    "XJA1VP": {  # CLIO V
        "support-endpoint-hvac-status": False,
    },
    "XJB1SU": {  # CAPTUR II
        "support-endpoint-hvac-status": False,
    },
    "XBG1VE": {  # DACIA SPRING
        "control-charge-via-kcm": True,
    },
    "XCB1VE": {  # MEGANE E-TECH
        "support-endpoint-lock-status": False,
    },
    "XCB1SE": {  # SCENIC E-TECH
        "support-endpoint-lock-status": False,
    },
}

GATEWAY_SPECIFICATIONS: dict[str, dict[str, Any]] = {
    "GDC": {  # ZOE phase 1
        "reports-charge-session-durations-in-minutes": True,
        "reports-in-watts": True,
        "support-endpoint-location": False,
        "support-endpoint-lock-status": False,
    },
}


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
        raise exceptions.KamereonResponseException(
            self.errorCode, error_details
        )  # pragma: no cover

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
        return False  # pragma: no cover

    def reports_charging_power_in_watts(self) -> bool:
        """Return True if model reports chargingInstantaneousPower in watts."""
        # Default to False for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.model.code, {}
            ).get("reports-in-watts", False)
        return False  # pragma: no cover

    def supports_endpoint(self, endpoint: str) -> bool:
        """Return True if model supports specified endpoint."""
        # Default to True for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.model.code, {}
            ).get(f"support-endpoint-{endpoint}", True)
        return True  # pragma: no cover

    def warns_on_method(self, method: str) -> str | None:
        """Return warning message if model trigger a warning on the method call."""
        # Default to None for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.model.code, {}
            ).get(f"warns-on-method-{method}", None)
        return None  # pragma: no cover

    def controls_action_via_kcm(self, action: str) -> bool:
        """Return True if model uses endpoint via kcm."""
        # Default to False for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.model.code, {}
            ).get(f"control-{action}-via-kcm", False)
        return False  # pragma: no cover


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
        except ValueError as err:  # pragma: no cover
            # should we return PlugState.NOT_AVAILABLE?
            raise exceptions.KamereonException(
                f"Unable to convert `{self.plugStatus}` to PlugState."
            ) from err

    def get_charging_status(self) -> enums.ChargeState | None:
        """Return charging status."""
        try:
            return (
                enums.ChargeState(self.chargingStatus)
                if self.chargingStatus is not None
                else None
            )
        except ValueError as err:  # pragma: no cover
            # should we return ChargeState.NOT_AVAILABLE?
            raise exceptions.KamereonException(
                f"Unable to convert `{self.chargingStatus}` to ChargeState."
            ) from err


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
        return False  # pragma: no cover

    def supports_endpoint(self, endpoint: str) -> bool:
        """Return True if model supports specified endpoint."""
        # Default to True for unknown vehicles
        if self.carGateway:
            return GATEWAY_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.carGateway, {}
            ).get(f"support-endpoint-{endpoint}", True)
        return True  # pragma: no cover

    def controls_action_via_kcm(self, action: str) -> bool:
        """Return True if model uses endpoint via kcm."""
        # Default to False for unknown vehicles
        if self.modelCodeDetail:
            return VEHICLE_SPECIFICATIONS.get(  # type:ignore[no-any-return]
                self.modelCodeDetail, {}
            ).get(f"control-{action}-via-kcm", False)
        return False  # pragma: no cover


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
        if self.startTime is None:  # pragma: no cover
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
        if "id" not in args:  # pragma: no cover
            raise ValueError("id not provided for update.")
        if self.schedules is None:  # pragma: no cover
            self.schedules = []
        for schedule in self.schedules:
            if schedule.id == args["id"]:  # pragma: no branch
                helpers.update_charge_schedule(schedule, args)
                return
        self.schedules.append(helpers.create_charge_schedule(args))  # pragma: no cover


@dataclass
class KamereonVehicleHvacSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-settings (mode+schedules) attributes."""

    mode: str | None
    schedules: list[HvacSchedule] | None

    def update(self, args: dict[str, Any]) -> None:
        """Update schedule."""
        if "id" not in args:  # pragma: no cover
            raise ValueError("id not provided for update.")
        if self.schedules is None:  # pragma: no cover
            self.schedules = []
        for schedule in self.schedules:
            if schedule.id == args["id"]:  # pragma: no branch
                helpers.update_hvac_schedule(schedule, args)
                return
        self.schedules.append(helpers.create_hvac_schedule(args))  # pragma: no cover


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
