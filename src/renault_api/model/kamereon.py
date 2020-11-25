"""Kamereon models."""
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import cast
from typing import Dict
from typing import List
from typing import Optional

import marshmallow_dataclass
from marshmallow.schema import Schema

from . import BaseModel
from . import BaseSchema
from renault_api.exceptions import KamereonException
from renault_api.exceptions import KamereonResponseException


@dataclass
class KamereonResponseError(BaseModel):
    """Kamereon response error."""

    errorCode: Optional[str]  # noqa: N815
    errorMessage: Optional[str]  # noqa: N815

    def raise_for_error_code(self) -> None:
        """Raise exception from response error."""
        raise KamereonResponseException(self.errorCode, self.get_error_details())

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
            raise KamereonException("`accountId` is None in KamereonPersonAccount.")
        return self.accountId


@dataclass
class KamereonPersonResponse(KamereonResponse):
    """Kamereon response to GET on /persons/{gigya_person_id}."""

    accounts: List[KamereonPersonAccount]


KamereonPersonResponseSchema = marshmallow_dataclass.class_schema(
    KamereonPersonResponse, base_schema=BaseSchema
)()


@dataclass
class KamereonVehiclesLink(BaseModel):
    """Kamereon account data."""

    vin: Optional[str]

    def get_vin(self) -> str:
        """Return jwt token."""
        if self.vin is None:  # pragma: no cover
            raise KamereonException("`vin` is None in KamereonVehiclesLink.")
        return self.vin


@dataclass
class KamereonVehiclesResponse(KamereonResponse):
    """Kamereon response to GET on /accounts/{account_id}/vehicles."""

    accountId: Optional[str]  # noqa: N815
    country: Optional[str]
    vehicleLinks: List[KamereonVehiclesLink]  # noqa: N815


KamereonVehiclesResponseSchema = marshmallow_dataclass.class_schema(
    KamereonVehiclesResponse, base_schema=BaseSchema
)()


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
            raise KamereonException("`data` is None in KamereonVehicleData.")
        if self.data.attributes is None:  # pragma: no cover
            raise KamereonException("`data.attributes` is None in KamereonVehicleData.")
        return cast(KamereonVehicleDataAttributes, schema.load(self.data.attributes))


KamereonVehicleDataResponseSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleDataResponse, base_schema=BaseSchema
)()


class ChargeState(Enum):
    """Enum for battery-status charge state."""

    NOT_IN_CHARGE = 0.0
    WAITING_FOR_PLANNED_CHARGE = 0.1
    CHARGE_ENDED = 0.2
    WAITING_FOR_CURRENT_CHARGE = 0.3
    ENERGY_FLAP_OPENED = 0.4
    CHARGE_IN_PROGRESS = 1.0
    # This next is more accurately "not charging" (<= ZE40) or "error" (ZE50).
    CHARGE_ERROR = -1.0
    NOT_AVAILABLE = -1.1


class PlugState(Enum):
    """Enum for battery-status plug state."""

    UNPLUGGED = 0
    PLUGGED = 1
    PLUG_ERROR = -1
    NOT_AVAILABLE = -2147483648


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

    def get_plug_status(self) -> Optional[PlugState]:
        """Return plug status."""
        if "plugStatus" not in self.raw_data:  # pragma: no cover
            raise KamereonException("`plugStatus` is None in KamereonVehicleData.")
        try:
            return PlugState(self.plugStatus)
        except ValueError:  # pragma: no cover
            # should we return PlugState.NOT_AVAILABLE?
            raise KamereonException(
                f"Unable to convert `{self.plugStatus}` to PlugState."
            )

    def get_charging_status(self) -> Optional[ChargeState]:
        """Return charging status."""
        if "chargingStatus" not in self.raw_data:  # pragma: no cover
            raise KamereonException("`chargingStatus` is None in KamereonVehicleData.")
        try:
            return ChargeState(self.chargingStatus)
        except ValueError:  # pragma: no cover
            # should we return ChargeState.NOT_AVAILABLE?
            raise KamereonException(
                f"Unable to convert `{self.chargingStatus}` to ChargeState."
            )


KamereonVehicleBatteryStatusDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleBatteryStatusData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleLocationData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data location attributes."""

    lastUpdateTime: Optional[str]  # noqa: N815
    gpsLatitude: Optional[float]  # noqa: N815
    gpsLongitude: Optional[float]  # noqa: N815


KamereonVehicleLocationDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleLocationData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleHvacStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-status attributes."""

    externalTemperature: Optional[float]  # noqa: N815
    hvacStatus: Optional[str]  # noqa: N815


KamereonVehicleHvacStatusDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleHvacStatusData, base_schema=BaseSchema
)()


class ChargeMode(Enum):
    """Enum for charge-mode."""

    ALWAYS = "always"
    ALWAYS_CHARGING = "always_charging"
    SCHEDULE_MODE = "schedule_mode"


@dataclass
class KamereonVehicleChargeModeData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charge-mode attributes."""

    chargeMode: Optional[str]  # noqa: N815

    def get_charge_mode(self) -> Optional[ChargeMode]:
        """Return charge mode."""
        if "chargeMode" not in self.raw_data:  # pragma: no cover
            raise KamereonException("`chargeMode` is None in KamereonVehicleData.")
        try:
            return ChargeMode(self.chargeMode)
        except ValueError:  # pragma: no cover
            raise KamereonException(
                f"Unable to convert `{self.chargeMode}` to ChargeMode."
            )


KamereonVehicleChargeModeDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleChargeModeData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleCockpitData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data cockpit attributes."""

    fuelAutonomy: Optional[float]  # noqa: N815
    fuelQuantity: Optional[float]  # noqa: N815
    totalMileage: Optional[float]  # noqa: N815


KamereonVehicleCockpitDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleCockpitData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleLockStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data lock-status attributes."""


KamereonVehicleLockStatusDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleLockStatusData, base_schema=BaseSchema
)()


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


KamereonVehicleChargingSettingsDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleChargingSettingsData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleNotificationSettingsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data notification-settings attributes."""


KamereonVehicleNotificationSettingsDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleNotificationSettingsData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleChargeHistoryData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charge-history attributes."""


KamereonVehicleChargeHistoryDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleChargeHistoryData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleChargesData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data charges attributes."""


KamereonVehicleChargesDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleChargesData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleHvacHistoryData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-history attributes."""


KamereonVehicleHvacHistoryDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleHvacHistoryData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleHvacSessionsData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data hvac-sessions attributes."""


KamereonVehicleHvacSessionsDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleHvacSessionsData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleHvacStartActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data hvac-start attributes."""


KamereonVehicleHvacStartActionDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleHvacStartActionData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleChargeScheduleActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charge-schedule attributes."""


KamereonVehicleChargeScheduleActionDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleChargeScheduleActionData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleChargeModeActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charge-mode attributes."""


KamereonVehicleChargeModeActionDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleChargeModeActionData, base_schema=BaseSchema
)()


@dataclass
class KamereonVehicleChargingStartActionData(KamereonVehicleDataAttributes):
    """Kamereon vehicle action data charging-start attributes."""


KamereonVehicleChargingStartActionDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleChargingStartActionData, base_schema=BaseSchema
)()
