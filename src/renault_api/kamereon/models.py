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
from renault_api.models import BaseModel

COMMON_ERRRORS = [
    {
        "errorCode": "err.func.403",
        "error_details": "Access is denied for this resource",
        "error_type": exceptions.AccessDeniedException,
    },
    {
        "errorCode": "err.tech.500",
        "error_details": "Invalid response from the upstream server"
        " (The request sent to the GDC is erroneous) ; 502 Bad Gateway",
        "error_type": exceptions.InvalidUpstreamException,
    },
    {
        "errorCode": "err.tech.501",
        "error_details": "This feature is not technically supported by this gateway",
        "error_type": exceptions.NotSupportedException,
    },
    {
        "errorCode": "err.func.wired.overloaded",
        "error_details": "You have reached your quota limit",
        "error_type": exceptions.QuotaLimitException,
    },
]


@dataclass
class KamereonResponseError(BaseModel):
    """Kamereon response error."""

    errorCode: Optional[str]  # noqa: N815
    errorMessage: Optional[str]  # noqa: N815

    def raise_for_error_code(self) -> None:
        """Raise exception from response error."""
        error_details = self.get_error_details()
        for common_error in COMMON_ERRRORS:
            if (
                self.errorCode == common_error["errorCode"]
                and error_details == common_error["error_details"]
            ):
                raise common_error["error_type"](self.errorCode, error_details)
        raise exceptions.KamereonResponseException(self.errorCode, error_details)

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
    """Kamereon account data."""

    accountId: Optional[str]  # noqa: N815
    accountType: Optional[str]  # noqa: N815
    accountStatus: Optional[str]  # noqa: N815

    def get_account_id(self) -> str:
        """Return jwt token."""
        if self.accountId is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`accountId` is None in KamereonPersonAccount."
            )
        return self.accountId


@dataclass
class KamereonPersonResponse(KamereonResponse):
    """Kamereon response to GET on /persons/{gigya_person_id}."""

    accounts: List[KamereonPersonAccount]


@dataclass
class KamereonVehiclesDetailsGroup(BaseModel):
    """Kamereon account data."""

    code: Optional[str]
    label: Optional[str]
    group: Optional[str]


@dataclass
class KamereonVehiclesDetails(BaseModel):
    """Kamereon account data."""

    vin: Optional[str]
    registrationNumber: Optional[str]  # noqa: N815
    brand: Optional[KamereonVehiclesDetailsGroup]
    model: Optional[KamereonVehiclesDetailsGroup]
    energy: Optional[KamereonVehiclesDetailsGroup]

    def get_vin(self) -> str:
        """Return vehicle vin."""
        if self.vin is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`vin` is None in KamereonVehiclesDetails."
            )
        return self.vin

    def get_registration_number(self) -> str:
        """Return vehicle vin."""
        if self.registrationNumber is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`registrationNumber` is None in KamereonVehiclesDetails."
            )
        return self.registrationNumber

    def get_energy_code(self) -> enums.EnergyCode:
        """Return vehicle energy code."""
        if self.energy is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`energy` is None in KamereonVehiclesDetails."
            )
        if self.energy.code is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`energy.code` is None in KamereonVehiclesDetails."
            )
        try:
            return enums.EnergyCode(self.energy.code)
        except ValueError:  # pragma: no cover
            raise exceptions.KamereonException(
                f"Unable to convert `{self.energy.code}` to EnergyCode."
            )

    def get_brand_label(self) -> str:
        """Return vehicle model label."""
        if self.brand is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`brand` is None in KamereonVehiclesDetails."
            )
        if self.brand.label is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`brand.label` is None in KamereonVehiclesDetails."
            )
        return self.brand.label

    def get_model_label(self) -> str:
        """Return vehicle model label."""
        if self.model is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`model` is None in KamereonVehiclesDetails."
            )
        if self.model.label is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`model.label` is None in KamereonVehiclesDetails."
            )
        return self.model.label


@dataclass
class KamereonVehiclesLink(BaseModel):
    """Kamereon vehicles link data."""

    vin: Optional[str]
    vehicleDetails: Optional[KamereonVehiclesDetails]  # noqa: N815

    def get_vin(self) -> str:
        """Return vehicle vin."""
        if self.vin is None:  # pragma: no cover
            raise exceptions.KamereonException("`vin` is None in KamereonVehiclesLink.")
        return self.vin

    def get_details(self) -> KamereonVehiclesDetails:
        """Return vehicle details."""
        if self.vehicleDetails is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`vehicleDetails` is None in KamereonVehiclesLink."
            )
        return self.vehicleDetails


@dataclass
class KamereonVehiclesResponse(KamereonResponse):
    """Kamereon response to GET on /accounts/{account_id}/vehicles."""

    accountId: Optional[str]  # noqa: N815
    country: Optional[str]
    vehicleLinks: List[KamereonVehiclesLink]  # noqa: N815


@dataclass
class KamereonVehicleDataAttributes(BaseModel):
    """Kamereon vehicle data."""


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

    def get_attributes(self, schema: Schema) -> KamereonVehicleDataAttributes:
        """Return jwt token."""
        if self.data is None:  # pragma: no cover
            raise exceptions.KamereonException("`data` is None in KamereonVehicleData.")
        if self.data.attributes is None:  # pragma: no cover
            raise exceptions.KamereonException(
                "`data.attributes` is None in KamereonVehicleData."
            )
        return cast(KamereonVehicleDataAttributes, schema.load(self.data.attributes))


@dataclass
class KamereonVehicleBatteryStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle battery-status data."""

    timestamp: Optional[str]
    batteryLevel: Optional[int]  # noqa: N815
    batteryTemperature: Optional[int]  # noqa: N815
    batteryAutonomy: Optional[int]  # noqa: N815
    batteryCapacity: Optional[int]  # noqa: N815
    batteryAvailableEnergy: Optional[int]  # noqa: N815
    plugStatus: Optional[int]  # noqa: N815
    chargingStatus: Optional[float]  # noqa: N815
    chargingRemainingTime: Optional[int]  # noqa: N815
    chargingInstantaneousPower: Optional[float]  # noqa: N815

    def get_plug_status(self) -> Optional[enums.PlugState]:
        """Return plug status."""
        if "plugStatus" not in self.raw_data:  # pragma: no cover
            raise exceptions.KamereonException(
                "`plugStatus` is None in KamereonVehicleData."
            )
        try:
            return enums.PlugState(self.plugStatus)
        except ValueError:  # pragma: no cover
            # should we return PlugState.NOT_AVAILABLE?
            raise exceptions.KamereonException(
                f"Unable to convert `{self.plugStatus}` to PlugState."
            )

    def get_charging_status(self) -> Optional[enums.ChargeState]:
        """Return charging status."""
        if "chargingStatus" not in self.raw_data:  # pragma: no cover
            raise exceptions.KamereonException(
                "`chargingStatus` is None in KamereonVehicleData."
            )
        try:
            return enums.ChargeState(self.chargingStatus)
        except ValueError:  # pragma: no cover
            # should we return ChargeState.NOT_AVAILABLE?
            raise exceptions.KamereonException(
                f"Unable to convert `{self.chargingStatus}` to ChargeState."
            )


@dataclass
class KamereonVehicleLocationData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data location attributes."""

    lastUpdateTime: Optional[str]  # noqa: N815
    gpsLatitude: Optional[float]  # noqa: N815
    gpsLongitude: Optional[float]  # noqa: N815


@dataclass
class KamereonVehicleHvacStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-status attributes."""

    externalTemperature: Optional[float]  # noqa: N815
    hvacStatus: Optional[str]  # noqa: N815


@dataclass
class KamereonVehicleChargeModeData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charge-mode attributes."""

    chargeMode: Optional[str]  # noqa: N815

    def get_charge_mode(self) -> Optional[enums.ChargeMode]:
        """Return charge mode."""
        if "chargeMode" not in self.raw_data:  # pragma: no cover
            raise exceptions.KamereonException(
                "`chargeMode` is None in KamereonVehicleData."
            )
        try:
            return enums.ChargeMode(self.chargeMode)
        except ValueError:  # pragma: no cover
            raise exceptions.KamereonException(
                f"Unable to convert `{self.chargeMode}` to ChargeMode."
            )


@dataclass
class KamereonVehicleCockpitData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data cockpit attributes."""

    fuelAutonomy: Optional[float]  # noqa: N815
    fuelQuantity: Optional[float]  # noqa: N815
    totalMileage: Optional[float]  # noqa: N815


@dataclass
class KamereonVehicleLockStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data lock-status attributes."""


@dataclass
class ChargeDaySchedule(BaseModel):
    """Kamereon vehicle charge schedule for day."""

    startTime: Optional[str]  # noqa: N815
    duration: Optional[int]

    def for_json(self) -> Dict[str, Any]:
        """Create dict for json."""
        return {
            "startTime": self.startTime,
            "duration": self.duration,
        }


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
        return {
            "id": self.id,
            "activated": self.activated,
            "monday": self.monday.for_json() if self.monday else {},
            "tuesday": self.tuesday.for_json() if self.tuesday else {},
            "wednesday": self.wednesday.for_json() if self.wednesday else {},
            "thursday": self.thursday.for_json() if self.thursday else {},
            "friday": self.friday.for_json() if self.friday else {},
            "saturday": self.saturday.for_json() if self.saturday else {},
            "sunday": self.sunday.for_json() if self.sunday else {},
        }


@dataclass
class KamereonVehicleChargingSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charging-settings attributes."""

    mode: Optional[str]
    schedules: Optional[List[ChargeSchedule]]


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
class KamereonVehicleChargeScheduleActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charge-schedule attributes."""


@dataclass
class KamereonVehicleChargeModeActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charge-mode attributes."""


@dataclass
class KamereonVehicleChargingStartActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charging-start attributes."""
