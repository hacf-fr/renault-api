"""Kamereon models."""
from dataclasses import dataclass
from typing import List
from typing import Optional

import marshmallow_dataclass

from . import BaseSchema


@dataclass
class KamereonPersonAccount:
    """Kamereon account data."""

    accountId: Optional[str]  # noqa: N815
    accountType: Optional[str]  # noqa: N815
    accountStatus: Optional[str]  # noqa: N815


@dataclass
class KamereonPersonResponse:
    """Kamereon response to GET on /persons/{gigya_person_id}."""

    accounts: List[KamereonPersonAccount]


@dataclass
class KamereonVehiclesLink:
    """Kamereon account data."""

    vin: Optional[str]


@dataclass
class KamereonVehiclesResponse:
    """Kamereon response to GET on /accounts/{account_id}/vehicles."""

    vehicleLinks: List[KamereonVehiclesLink]  # noqa: N815


KamereonPersonResponseSchema = marshmallow_dataclass.class_schema(
    KamereonPersonResponse, base_schema=BaseSchema
)()
KamereonVehiclesResponseSchema = marshmallow_dataclass.class_schema(
    KamereonVehiclesResponse, base_schema=BaseSchema
)()
