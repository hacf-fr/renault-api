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
        if not self.accountId:  # pragma: no cover
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
        if not self.vin:  # pragma: no cover
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
        if not self.data:  # pragma: no cover
            raise KamereonException("`data` is None in KamereonVehicleData.")
        if not self.data.attributes:  # pragma: no cover
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
    batteryAutonomy: Optional[int]  # noqa: N815
    batteryCapacity: Optional[int]  # noqa: N815
    batteryAvailableEnergy: Optional[int]  # noqa: N815
    plugStatus: Optional[int]  # noqa: N815
    chargingStatus: Optional[float]  # noqa: N815

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
        """Return plug status."""
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
class KamereonVehicleHvacStatusData(KamereonVehicleDataAttributes):
    """Kamereon vehicle data battery-status attributes."""

    externalTemperature: Optional[float]  # noqa: N815
    hvacStatus: Optional[str]  # noqa: N815


KamereonVehicleHvacStatusDataSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleHvacStatusData, base_schema=BaseSchema
)()
