"""Gigya schemas."""
import marshmallow_dataclass

from . import models
from renault_api.models import BaseSchema


GigyaResponseSchema = marshmallow_dataclass.class_schema(
    models.GigyaResponse, base_schema=BaseSchema
)()


GigyaLoginResponseSchema = marshmallow_dataclass.class_schema(
    models.GigyaLoginResponse, base_schema=BaseSchema
)()


GigyaGetAccountInfoResponseSchema = marshmallow_dataclass.class_schema(
    models.GigyaGetAccountInfoResponse, base_schema=BaseSchema
)()


GigyaGetJWTResponseSchema = marshmallow_dataclass.class_schema(
    models.GigyaGetJWTResponse, base_schema=BaseSchema
)()
