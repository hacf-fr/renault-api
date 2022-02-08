"""Kamereon schemas."""
import marshmallow_dataclass

from . import models
from renault_api.models import BaseSchema


KamereonResponseSchema = marshmallow_dataclass.class_schema(
    models.KamereonResponse, base_schema=BaseSchema
)()


KamereonPersonResponseSchema = marshmallow_dataclass.class_schema(
    models.KamereonPersonResponse, base_schema=BaseSchema
)()


KamereonVehicleContractsResponseSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleContractsResponse, base_schema=BaseSchema
)()

KamereonVehiclesResponseSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehiclesResponse, base_schema=BaseSchema
)()

KamereonVehicleDetailsResponseSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleDetailsResponse, base_schema=BaseSchema
)()


KamereonVehicleDataResponseSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleDataResponse, base_schema=BaseSchema
)()


KamereonVehicleBatteryStatusDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleBatteryStatusData, base_schema=BaseSchema
)()


KamereonVehicleLocationDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleLocationData, base_schema=BaseSchema
)()

KamereonVehicleLockStatusDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleLockStatusData, base_schema=BaseSchema
)()

KamereonVehicleResStateDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleResStateData, base_schema=BaseSchema
)()

KamereonVehicleHvacStatusDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleHvacStatusData, base_schema=BaseSchema
)()


KamereonVehicleChargeModeDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleChargeModeData, base_schema=BaseSchema
)()


KamereonVehicleCockpitDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleCockpitData, base_schema=BaseSchema
)()


KamereonVehicleLockStatusDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleLockStatusData, base_schema=BaseSchema
)()


KamereonVehicleCarAdapterDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleCarAdapterData, base_schema=BaseSchema
)()


KamereonVehicleChargingSettingsDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleChargingSettingsData, base_schema=BaseSchema
)()

KamereonVehicleHvacSettingsDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleHvacSettingsData, base_schema=BaseSchema
)()

KamereonVehicleNotificationSettingsDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleNotificationSettingsData, base_schema=BaseSchema
)()


KamereonVehicleChargeHistoryDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleChargeHistoryData, base_schema=BaseSchema
)()


KamereonVehicleChargesDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleChargesData, base_schema=BaseSchema
)()


KamereonVehicleHvacHistoryDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleHvacHistoryData, base_schema=BaseSchema
)()


KamereonVehicleHvacSessionsDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleHvacSessionsData, base_schema=BaseSchema
)()


KamereonVehicleHvacStartActionDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleHvacStartActionData, base_schema=BaseSchema
)()

KamereonVehicleHvacScheduleActionDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleHvacScheduleActionData, base_schema=BaseSchema
)()

KamereonVehicleChargeScheduleActionDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleChargeScheduleActionData, base_schema=BaseSchema
)()


KamereonVehicleChargeModeActionDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleChargeModeActionData, base_schema=BaseSchema
)()


KamereonVehicleChargingStartActionDataSchema = marshmallow_dataclass.class_schema(
    models.KamereonVehicleChargingStartActionData, base_schema=BaseSchema
)()
