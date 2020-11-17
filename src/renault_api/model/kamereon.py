"""Kamereon models."""
import json
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import marshmallow_dataclass

from . import BaseSchema
from renault_api.exceptions import KamereonResponseException


@dataclass
class KamereonResponseError:
    """Kamereon response."""

    errorCode: Optional[str]  # noqa: N815
    errorMessage: Optional[str]  # noqa: N815

    def raise_for_error_code(self) -> None: 
        """Checks the response information."""
        if self.errorCode == "err.func.400":
            raise KamereonResponseException(self.errorCode, self.errorMessage)
        if self.errorCode == "err.tech.500":
            raise KamereonResponseException(self.errorCode, self.errorMessage)
        if self.errorCode == "err.tech.501":
            raise KamereonResponseException(self.errorCode, self.errorMessage)
        if self.errorCode == "err.func.wired.overloaded":
            raise KamereonResponseException(self.errorCode, self.errorMessage)
    
    def get_error_details(error_message: str)-> Optional[str]:
        if not error_message:
            return
        try:
            error_details = json.loads(error_message)
        except json.JSONDecodeError:
            return error_message
        
        for inner_error_details in error_details.get("errors", []):
            if "detail" in inner_error_details:
                return inner_error_details["detail"]
            if "title" in inner_error_details:
                return inner_error_details["title"]

@dataclass
class KamereonResponse:
    """Kamereon response."""

    errors: Optional[List[KamereonResponseError]]

    def raise_for_error_code(self) -> None:
        """Checks the response information."""
        if self.errors:
            for error in self.errors:
                error.raise_for_error_code()


@dataclass
class KamereonPersonAccount:
    """Kamereon account data."""

    accountId: Optional[str]  # noqa: N815
    accountType: Optional[str]  # noqa: N815
    accountStatus: Optional[str]  # noqa: N815


@dataclass
class KamereonPersonResponse(KamereonResponse):
    """Kamereon response to GET on /persons/{gigya_person_id}."""

    accounts: List[KamereonPersonAccount]


@dataclass
class KamereonVehiclesLink:
    """Kamereon account data."""

    vin: Optional[str]


@dataclass
class KamereonVehiclesResponse(KamereonResponse):
    """Kamereon response to GET on /accounts/{account_id}/vehicles."""

    accountId: Optional[str]  # noqa: N815
    country: Optional[str]
    vehicleLinks: List[KamereonVehiclesLink]  # noqa: N815


@dataclass
class KamereonVehicleData:
    """Kamereon account data."""

    type: Optional[str]
    id: Optional[str]
    attributes: Optional[Dict[str, Any]]


@dataclass
class KamereonVehicleDataResponse(KamereonResponse):
    """Kamereon response to GET/POST on .../cars/{vin}/{type}."""

    data: Optional[KamereonVehicleData]


KamereonPersonResponseSchema = marshmallow_dataclass.class_schema(
    KamereonPersonResponse, base_schema=BaseSchema
)()
KamereonVehiclesResponseSchema = marshmallow_dataclass.class_schema(
    KamereonVehiclesResponse, base_schema=BaseSchema
)()
KamereonVehicleDataResponseSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleDataResponse, base_schema=BaseSchema
)()
