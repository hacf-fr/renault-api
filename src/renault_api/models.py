"""Models for Renault API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import marshmallow


@dataclass
class BaseModel:
    """Base model for Gigya and Kamereon models to include raw_data."""

    raw_data: dict[str, Any]


class BaseSchema(marshmallow.Schema):
    """Base schema for Gigya and Kamereon models to exclude unknown fields."""

    class Meta:
        """Force unknown fields to 'exclude'."""

        unknown = marshmallow.EXCLUDE

    @marshmallow.pre_load
    def get_raw_data(self, data, **kwargs):  # type: ignore
        """Ensure raw_data is added to the data set."""
        return {"raw_data": data, **data}
