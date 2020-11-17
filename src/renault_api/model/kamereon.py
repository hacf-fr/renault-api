"""Kamereon models."""
from dataclasses import dataclass
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import marshmallow_dataclass

from . import BaseSchema


@dataclass
class KamereonResponseError:
    """Kamereon response."""

    errorCode: Optional[str]  # noqa: N815
    errorMessage: Optional[str]  # noqa: N815


@dataclass
class KamereonResponse:
    """Kamereon response."""

    errors: Optional[List[KamereonResponseError]]


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

    data: KamereonVehicleData


KamereonPersonResponseSchema = marshmallow_dataclass.class_schema(
    KamereonPersonResponse, base_schema=BaseSchema
)()
KamereonVehiclesResponseSchema = marshmallow_dataclass.class_schema(
    KamereonVehiclesResponse, base_schema=BaseSchema
)()
KamereonVehicleDataResponseSchema = marshmallow_dataclass.class_schema(
    KamereonVehicleDataResponse, base_schema=BaseSchema
)()
