"""Kamereon models."""
import json
from dataclasses import dataclass
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Optional

from marshmallow.schema import Schema

from . import enums
from . import exceptions
from . import helpers
from .enums import AssetPictureSize
from renault_api.models import BaseModel

COMMON_ERRRORS: List[Dict[str, Any]] = [
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

VEHICLE_SPECIFICATIONS: Dict[str, Dict[str, Any]] = {
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
}

GATEWAY_SPECIFICATIONS: Dict[str, Dict[str, Any]] = {
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

    errorCode: Optional[str]
    errorMessage: Optional[str]

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

    def get_error_details(self) -> Optional[str]:
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

    errors: Optional[List[KamereonResponseError]]

    def raise_for_error_code(self) -> None:
        """Raise exception if errors found in the response."""
        for error in self.errors or []:
            # Until we have a sample for multiple errors, just raise on first one
            error.raise_for_error_code()


@dataclass
class KamereonPersonAccount(BaseModel):
    """Kamereon person account data."""

    accountId: Optional[str]
    accountType: Optional[str]
    accountStatus: Optional[str]


@dataclass
class KamereonPersonResponse(KamereonResponse):
    """Kamereon response to GET on /persons/{gigya_person_id}."""

    accounts: Optional[List[KamereonPersonAccount]]


@dataclass
class KamereonVehicleDetailsGroup(BaseModel):
    """Kamereon vehicle details group data."""

    code: Optional[str]
    label: Optional[str]
    group: Optional[str]


@dataclass
class KamereonVehicleDetails(BaseModel):
    """Kamereon vehicle details."""

    vin: Optional[str]
    registrationNumber: Optional[str]
    radioCode: Optional[str]
    brand: Optional[KamereonVehicleDetailsGroup]
    model: Optional[KamereonVehicleDetailsGroup]
    energy: Optional[KamereonVehicleDetailsGroup]
    engineEnergyType: Optional[str]
    assets: Optional[List[Dict[str, Any]]]

    def get_energy_code(self) -> Optional[str]:
        """Return vehicle energy code."""
        return self.energy.code if self.energy else None

    def get_brand_label(self) -> Optional[str]:
        """Return vehicle model label."""
        return self.brand.label if self.brand else None

    def get_model_code(self) -> Optional[str]:
        """Return vehicle model code."""
        return self.model.code if self.model else None

    def get_model_label(self) -> Optional[str]:
        """Return vehicle model label."""
        return self.model.label if self.model else None

    def get_asset(self, asset_type: str) -> Optional[Dict[str, Any]]:
        """Return asset."""
        return next(
            filter(
                lambda asset: asset.get("assetType") == asset_type, self.assets or []
            )
        )

    def get_picture(
        self, size: AssetPictureSize = AssetPictureSize.LARGE
    ) -> Optional[str]:
        """Return vehicle picture."""
        asset: Dict[str, Any] = self.get_asset("PICTURE") or {}

        rendition: Dict[str, str] = next(
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
            return VEHICLE_SPECIFICATIONS.get(self.model.code, {}).get(
                "reports-charge-session-durations-in-minutes", False
            )
        return False  # pragma: no cover

    def reports_charging_power_in_watts(self) -> bool:
        """Return True if model reports chargingInstantaneousPower in watts."""
        # Default to False for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(self.model.code, {}).get(
                "reports-in-watts", False
            )
        return False  # pragma: no cover

    def supports_endpoint(self, endpoint: str) -> bool:
        """Return True if model supports specified endpoint."""
        # Default to True for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(self.model.code, {}).get(
                f"support-endpoint-{endpoint}", True
            )
        return True  # pragma: no cover

    def warns_on_method(self, method: str) -> Optional[str]:
        """Return warning message if model trigger a warning on the method call."""
        # Default to None for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(self.model.code, {}).get(
                f"warns-on-method-{method}", None
            )
        return None  # pragma: no cover

    def controls_action_via_kcm(self, action: str) -> bool:
        """Return True if model uses endpoint via kcm."""
        # Default to False for unknown vehicles
        if self.model and self.model.code:
            return VEHICLE_SPECIFICATIONS.get(self.model.code, {}).get(
                f"control-{action}-via-kcm", False
            )
        return False  # pragma: no cover


@dataclass
class KamereonVehiclesLink(BaseModel):
    """Kamereon vehicles link data."""

    vin: Optional[str]
    vehicleDetails: Optional[KamereonVehicleDetails]


@dataclass
class KamereonVehiclesResponse(KamereonResponse):
    """Kamereon response to GET on /accounts/{account_id}/vehicles."""

    accountId: Optional[str]
    country: Optional[str]
    vehicleLinks: Optional[List[KamereonVehiclesLink]]


@dataclass
class KamereonVehicleDetailsResponse(KamereonResponse, KamereonVehicleDetails):
    """Kamereon response to GET on /accounts/{account_id}/vehicles/{vin}/details."""


@dataclass
class KamereonVehicleDataAttributes(BaseModel):
    """Kamereon vehicle data attributes."""


@dataclass
class KamereonVehicleContract(BaseModel):
    """Kamereon vehicle contract."""

    type: Optional[str]
    contractId: Optional[str]
    code: Optional[str]
    group: Optional[str]
    durationMonths: Optional[int]
    startDate: Optional[str]
    endDate: Optional[str]
    status: Optional[str]
    statusLabel: Optional[str]
    description: Optional[str]


@dataclass
class KamereonVehicleContractsResponse(KamereonResponse):
    """Kamereon response to GET on /accounts/{accountId}/vehicles/{vin}/contracts."""

    contractList: Optional[List[KamereonVehicleContract]]


@dataclass
class KamereonVehicleData(BaseModel):
    """Kamereon vehicle data."""

    type: Optional[str]
    id: Optional[str]
    attributes: Optional[Dict[str, Any]]


@dataclass
class KamereonVehicleDataResponse(KamereonResponse):
    """Kamereon response to GET/POST on .../cars/{vin}/{type}."""

    data: Optional[KamereonVehicleData]

    def get_attributes(self, schema: Schema) -> Optional[KamereonVehicleDataAttributes]:
        """Return jwt token."""
        return (
            cast(KamereonVehicleDataAttributes, schema.load(self.data.attributes))
            if self.data and self.data.attributes is not None
            else None
        )


@dataclass
class KamereonVehicleBatteryStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle battery-status data."""

    timestamp: Optional[str]
    batteryLevel: Optional[int]
    batteryTemperature: Optional[int]
    batteryAutonomy: Optional[int]
    batteryCapacity: Optional[int]
    batteryAvailableEnergy: Optional[int]
    plugStatus: Optional[int]
    chargingStatus: Optional[float]
    chargingRemainingTime: Optional[int]
    chargingInstantaneousPower: Optional[float]

    def get_plug_status(self) -> Optional[enums.PlugState]:
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

    def get_charging_status(self) -> Optional[enums.ChargeState]:
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
class KamereonVehicleLocationData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data location attributes."""

    lastUpdateTime: Optional[str]
    gpsLatitude: Optional[float]
    gpsLongitude: Optional[float]


@dataclass
class KamereonVehicleHvacStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-status attributes."""

    lastUpdateTime: Optional[str]
    externalTemperature: Optional[float]
    hvacStatus: Optional[str]
    nextHvacStartDate: Optional[str]
    socThreshold: Optional[float]


@dataclass
class KamereonVehicleChargeModeData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charge-mode attributes."""

    chargeMode: Optional[str]


@dataclass
class KamereonVehicleCockpitData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data cockpit attributes."""

    fuelAutonomy: Optional[float]
    fuelQuantity: Optional[float]
    totalMileage: Optional[float]


@dataclass
class KamereonVehicleLockStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data lock-status attributes."""

    lockStatus: Optional[str]
    doorStatusRearLeft: Optional[str]
    doorStatusRearRight: Optional[str]
    doorStatusDriver: Optional[str]
    doorStatusPassenger: Optional[str]
    hatchStatus: Optional[str]
    lastUpdateTime: Optional[str]


@dataclass
class KamereonVehicleResStateData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data res-set attributes."""

    details: Optional[str]
    code: Optional[str]


@dataclass
class KamereonVehicleCarAdapterData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-status attributes."""

    vin: Optional[str]
    vehicleId: Optional[int]
    batteryCode: Optional[str]
    brand: Optional[str]
    canGeneration: Optional[str]
    carGateway: Optional[str]
    deliveryCountry: Optional[str]
    deliveryDate: Optional[str]
    energy: Optional[str]
    engineType: Optional[str]
    familyCode: Optional[str]
    firstRegistrationDate: Optional[str]
    gearbox: Optional[str]
    modelCode: Optional[str]
    modelCodeDetail: Optional[str]
    modelName: Optional[str]
    radioType: Optional[str]
    region: Optional[str]
    registrationCountry: Optional[str]
    registrationNumber: Optional[str]
    tcuCode: Optional[str]
    versionCode: Optional[str]
    privacyMode: Optional[str]
    privacyModeUpdateDate: Optional[str]
    svtFlag: Optional[bool]
    svtBlockFlag: Optional[bool]

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
            return GATEWAY_SPECIFICATIONS.get(self.carGateway, {}).get(
                "reports-in-watts", False
            )
        return False  # pragma: no cover

    def supports_endpoint(self, endpoint: str) -> bool:
        """Return True if model supports specified endpoint."""
        # Default to True for unknown vehicles
        if self.carGateway:
            return GATEWAY_SPECIFICATIONS.get(self.carGateway, {}).get(
                f"support-endpoint-{endpoint}", True
            )
        return True  # pragma: no cover

    def controls_action_via_kcm(self, action: str) -> bool:
        """Return True if model uses endpoint via kcm."""
        # Default to False for unknown vehicles
        if self.modelCodeDetail:
            return VEHICLE_SPECIFICATIONS.get(self.modelCodeDetail, {}).get(
                f"control-{action}-via-kcm", False
            )
        return False  # pragma: no cover


@dataclass
class ChargeDaySchedule(BaseModel):
    """Kamereon vehicle charge schedule for day."""

    startTime: Optional[str]
    duration: Optional[int]

    def for_json(self) -> Dict[str, Any]:
        """Create dict for json."""
        return {
            "startTime": self.startTime,
            "duration": self.duration,
        }

    def get_end_time(self) -> Optional[str]:
        """Get end time."""
        if self.startTime is None:  # pragma: no cover
            return None
        return helpers.get_end_time(self.startTime, self.duration)


@dataclass
class ChargeSchedule(BaseModel):
    """Kamereon vehicle charge schedule for week."""

    id: Optional[int]
    activated: Optional[bool]
    monday: Optional[ChargeDaySchedule]
    tuesday: Optional[ChargeDaySchedule]
    wednesday: Optional[ChargeDaySchedule]
    thursday: Optional[ChargeDaySchedule]
    friday: Optional[ChargeDaySchedule]
    saturday: Optional[ChargeDaySchedule]
    sunday: Optional[ChargeDaySchedule]

    def for_json(self) -> Dict[str, Any]:
        """Create dict for json."""
        result: Dict[str, Any] = {
            "id": self.id,
            "activated": self.activated,
        }
        for day in helpers.DAYS_OF_WEEK:
            day_spec: Optional[ChargeDaySchedule] = getattr(self, day, None)
            if day_spec is None:
                result[day] = day_spec
            else:
                result[day] = day_spec.for_json()
        return result


@dataclass
class HvacDaySchedule(BaseModel):
    """Kamereon vehicle hvac schedule for day."""

    readyAtTime: Optional[str]

    def for_json(self) -> Dict[str, Optional[str]]:
        """Create dict for json."""
        return {
            "readyAtTime": self.readyAtTime,
        }


@dataclass
class HvacSchedule(BaseModel):
    """Kamereon vehicle hvac schedule for week."""

    id: Optional[int]
    activated: Optional[bool]
    monday: Optional[HvacDaySchedule]
    tuesday: Optional[HvacDaySchedule]
    wednesday: Optional[HvacDaySchedule]
    thursday: Optional[HvacDaySchedule]
    friday: Optional[HvacDaySchedule]
    saturday: Optional[HvacDaySchedule]
    sunday: Optional[HvacDaySchedule]

    def for_json(self) -> Dict[str, Any]:
        """Create dict for json."""
        result: Dict[str, Any] = {
            "id": self.id,
            "activated": self.activated,
        }
        for day in helpers.DAYS_OF_WEEK:
            day_spec: Optional[HvacDaySchedule] = getattr(self, day, None)
            if day_spec is None:
                result[day] = day_spec
            else:
                result[day] = day_spec.for_json()
        return result


@dataclass
class KamereonVehicleChargingSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charging-settings attributes."""

    mode: Optional[str]
    schedules: Optional[List[ChargeSchedule]]

    def update(self, args: Dict[str, Any]) -> None:
        """Update schedule."""
        if "id" not in args:  # pragma: no cover
            raise ValueError("id not provided for update.")
        if self.schedules is None:  # pragma: no cover
            self.schedules = []
        for schedule in self.schedules:
            if schedule.id == args["id"]:  # pragma: no branch
                helpers.update_schedule(schedule, args)
                return
        self.schedules.append(helpers.create_schedule(args))  # pragma: no cover


@dataclass
class KamereonVehicleHvacSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-settings (mode+schedules) attributes."""

    mode: Optional[str]
    schedules: Optional[List[HvacSchedule]]


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
