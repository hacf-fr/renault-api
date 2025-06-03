"""Client for Renault API."""

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Optional
from typing import Union
from typing import cast

import aiohttp

from .credential_store import CredentialStore
from .exceptions import EndpointNotAvailableError
from .exceptions import RenaultException
from .kamereon import ACCOUNT_ENDPOINT_ROOT
from .kamereon import models
from .kamereon import schemas
from .renault_session import RenaultSession

PERIOD_DAY_FORMAT = "%Y%m%d"
PERIOD_MONTH_FORMAT = "%Y%m"
PERIOD_TZ_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
PERIOD_FORMATS = {"day": PERIOD_DAY_FORMAT, "month": PERIOD_MONTH_FORMAT}


class RenaultVehicle:
    """Proxy to a Renault vehicle."""

    def __init__(
        self,
        account_id: str,
        vin: str,
        *,
        session: Optional[RenaultSession] = None,
        websession: Optional[aiohttp.ClientSession] = None,
        locale: Optional[str] = None,
        country: Optional[str] = None,
        locale_details: Optional[dict[str, str]] = None,
        credential_store: Optional[CredentialStore] = None,
        vehicle_details: Optional[models.KamereonVehicleDetails] = None,
        car_adapter: Optional[models.KamereonVehicleCarAdapterData] = None,
    ) -> None:
        """Initialise Renault vehicle."""
        self._account_id = account_id
        self._vin = vin
        self._vehicle_details = vehicle_details
        self._car_adapter = car_adapter
        self._contracts: Optional[list[models.KamereonVehicleContract]] = None

        if session:
            self._session = session
        else:
            if websession is None:
                raise RenaultException(
                    "`websession` is required if session is not provided."
                )
            self._session = RenaultSession(
                websession=websession,
                locale=locale,
                country=country,
                locale_details=locale_details,
                credential_store=credential_store,
            )

    @property
    def session(self) -> RenaultSession:
        """Get session."""
        return self._session

    @property
    def account_id(self) -> str:
        """Get account id."""
        return self._account_id

    @property
    def vin(self) -> str:
        """Get vin."""
        return self._vin

    def _convert_variables(self, endpoint: str) -> str:
        """Replace account_id / vin"""
        return endpoint.replace("{account_id}", self.account_id).replace(
            "{vin}", self.vin
        )

    async def http_get(self, endpoint: str) -> models.KamereonResponse:
        """Run HTTP GET to endpoint."""
        endpoint = self._convert_variables(endpoint)
        return await self.session.http_request("GET", endpoint)

    async def http_post(
        self, endpoint: str, json: Optional[dict[str, Any]] = None
    ) -> models.KamereonResponse:
        """Run HTTP POST to endpoint."""
        endpoint = self._convert_variables(endpoint)
        return await self.session.http_request("POST", endpoint, json)

    async def get_full_endpoint(self, endpoint: str) -> str:
        """From VEHICLE_ENDPOINTS / DEFAULT_ENDPOINT."""
        endpoint_definition = await self.get_endpoint_definition(endpoint)
        return ACCOUNT_ENDPOINT_ROOT + endpoint_definition.endpoint

    async def get_endpoint_definition(self, endpoint: str) -> models.EndpointDefinition:
        """From VEHICLE_ENDPOINTS / DEFAULT_ENDPOINT."""
        details = await self.get_details()
        full_endpoint = details.get_endpoint(endpoint)
        if full_endpoint is None:
            raise EndpointNotAvailableError(endpoint, details.get_model_code())

        return full_endpoint

    async def _get_vehicle_data(
        self, endpoint: Union[str, models.EndpointDefinition]
    ) -> models.KamereonVehicleDataResponse:
        """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
        if isinstance(endpoint, models.EndpointDefinition):
            full_endpoint = ACCOUNT_ENDPOINT_ROOT + endpoint.endpoint
        else:
            full_endpoint = await self.get_full_endpoint(endpoint)
        response = await self.http_get(full_endpoint)
        return cast(
            models.KamereonVehicleDataResponse,
            schemas.KamereonVehicleDataResponseSchema.load(response.raw_data),
        )

    async def _set_vehicle_data(
        self,
        endpoint: Union[str, models.EndpointDefinition],
        json: Optional[dict[str, Any]],
    ) -> models.KamereonVehicleDataResponse:
        """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
        if isinstance(endpoint, models.EndpointDefinition):
            full_endpoint = ACCOUNT_ENDPOINT_ROOT + endpoint.endpoint
        else:
            full_endpoint = await self.get_full_endpoint(endpoint)
        response = await self.http_post(full_endpoint, json)
        return cast(
            models.KamereonVehicleDataResponse,
            schemas.KamereonVehicleDataResponseSchema.load(response.raw_data),
        )

    async def get_details(self) -> models.KamereonVehicleDetails:
        """Get vehicle details."""
        if self._vehicle_details:
            return self._vehicle_details

        response = await self.session.get_vehicle_details(
            account_id=self.account_id,
            vin=self.vin,
        )
        self._vehicle_details = cast(
            models.KamereonVehicleDetails,
            response,
        )
        return self._vehicle_details

    async def get_car_adapter(self) -> models.KamereonVehicleCarAdapterData:
        """Get vehicle car adapter details."""
        if self._car_adapter:
            return self._car_adapter

        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="",
        )
        self._car_adapter = cast(
            models.KamereonVehicleCarAdapterData,
            response.get_attributes(schemas.KamereonVehicleCarAdapterDataSchema),
        )
        return self._car_adapter

    async def get_contracts(self) -> list[models.KamereonVehicleContract]:
        """Get vehicle contracts."""
        if self._contracts:
            return self._contracts

        response = await self.session.get_vehicle_contracts(
            account_id=self.account_id,
            vin=self.vin,
        )
        if response.contractList is None:
            raise ValueError("response.contractList is None")
        self._contracts = response.contractList
        return self._contracts

    async def get_battery_status(self) -> models.KamereonVehicleBatteryStatusData:
        """Get vehicle battery status."""
        response = await self._get_vehicle_data("battery-status")
        return cast(
            models.KamereonVehicleBatteryStatusData,
            response.get_attributes(schemas.KamereonVehicleBatteryStatusDataSchema),
        )

    async def get_tyre_pressure(self) -> models.KamereonVehicleTyrePressureData:
        """Get vehicle tyre pressure."""
        response = await self._get_vehicle_data("pressure")
        return cast(
            models.KamereonVehicleTyrePressureData,
            response.get_attributes(schemas.KamereonVehicleTyrePressureDataSchema),
        )

    async def get_location(self) -> models.KamereonVehicleLocationData:
        """Get vehicle location."""
        response = await self._get_vehicle_data("location")
        return cast(
            models.KamereonVehicleLocationData,
            response.get_attributes(schemas.KamereonVehicleLocationDataSchema),
        )

    async def get_hvac_status(self) -> models.KamereonVehicleHvacStatusData:
        """Get vehicle hvac status."""
        response = await self._get_vehicle_data("hvac-status")
        return cast(
            models.KamereonVehicleHvacStatusData,
            response.get_attributes(schemas.KamereonVehicleHvacStatusDataSchema),
        )

    async def get_hvac_settings(self) -> models.KamereonVehicleHvacSettingsData:
        """Get vehicle hvac settings (schedule+mode)."""
        response = await self._get_vehicle_data("hvac-settings")
        return cast(
            models.KamereonVehicleHvacSettingsData,
            response.get_attributes(schemas.KamereonVehicleHvacSettingsDataSchema),
        )

    async def get_charge_mode(self) -> models.KamereonVehicleChargeModeData:
        """Get vehicle charge mode."""
        response = await self._get_vehicle_data("charge-mode")
        return cast(
            models.KamereonVehicleChargeModeData,
            response.get_attributes(schemas.KamereonVehicleChargeModeDataSchema),
        )

    async def get_cockpit(self) -> models.KamereonVehicleCockpitData:
        """Get vehicle cockpit."""
        response = await self._get_vehicle_data("cockpit")
        return cast(
            models.KamereonVehicleCockpitData,
            response.get_attributes(schemas.KamereonVehicleCockpitDataSchema),
        )

    async def get_lock_status(self) -> models.KamereonVehicleLockStatusData:
        """Get vehicle lock status."""
        response = await self._get_vehicle_data("lock-status")
        return cast(
            models.KamereonVehicleLockStatusData,
            response.get_attributes(schemas.KamereonVehicleLockStatusDataSchema),
        )

    async def get_res_state(self) -> models.KamereonVehicleResStateData:
        """Get vehicle res state."""
        response = await self._get_vehicle_data("res-state")
        return cast(
            models.KamereonVehicleResStateData,
            response.get_attributes(schemas.KamereonVehicleResStateDataSchema),
        )

    async def get_charge_schedule(self) -> dict[str, Any]:
        """Get vehicle charge schedule."""
        endpoint_definition = await self.get_endpoint_definition("charge-schedule")
        response = await self._get_vehicle_data(endpoint_definition)
        if endpoint_definition.mode == "kcm":
            return response.raw_data
        return response.raw_data["data"]["attributes"]  # type:ignore[no-any-return]

    async def get_notification_settings(
        self,
    ) -> models.KamereonVehicleNotificationSettingsData:
        """Get vehicle notification settings."""
        response = await self._get_vehicle_data("notification-settings")
        return cast(
            models.KamereonVehicleNotificationSettingsData,
            response.get_attributes(
                schemas.KamereonVehicleNotificationSettingsDataSchema
            ),
        )

    async def get_charge_history(
        self, start: datetime, end: datetime, period: str
    ) -> models.KamereonVehicleChargeHistoryData:
        """Get vehicle charge history."""
        if not isinstance(start, datetime):
            raise TypeError(
                "`start` should be an instance of datetime.datetime, "
                f"not {start.__class__}"
            )
        if not isinstance(end, datetime):
            raise TypeError(
                f"`end` should be an instance of datetime.datetime, not {end.__class__}"
            )
        if period not in PERIOD_FORMATS.keys():
            raise TypeError("`period` should be one of `month`, `day`")

        params = {
            "type": period,
            "start": start.strftime(PERIOD_FORMATS[period]),
            "end": end.strftime(PERIOD_FORMATS[period]),
        }
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="charge-history",
            params=params,
        )
        return cast(
            models.KamereonVehicleChargeHistoryData,
            response.get_attributes(schemas.KamereonVehicleChargeHistoryDataSchema),
        )

    async def get_charges(
        self, start: datetime, end: datetime
    ) -> models.KamereonVehicleChargesData:
        """Get vehicle charges."""
        if not isinstance(start, datetime):
            raise TypeError(
                "`start` should be an instance of datetime.datetime, "
                f"not {start.__class__}"
            )
        if not isinstance(end, datetime):
            raise TypeError(
                f"`end` should be an instance of datetime.datetime, not {end.__class__}"
            )

        params = {
            "start": start.strftime(PERIOD_DAY_FORMAT),
            "end": end.strftime(PERIOD_DAY_FORMAT),
        }
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="charges",
            params=params,
        )
        return cast(
            models.KamereonVehicleChargesData,
            response.get_attributes(schemas.KamereonVehicleChargesDataSchema),
        )

    async def get_hvac_history(
        self, start: datetime, end: datetime, period: str
    ) -> models.KamereonVehicleHvacHistoryData:
        """Get vehicle hvac history."""
        if not isinstance(start, datetime):
            raise TypeError(
                "`start` should be an instance of datetime.datetime, "
                f"not {start.__class__}"
            )
        if not isinstance(end, datetime):
            raise TypeError(
                f"`end` should be an instance of datetime.datetime, not {end.__class__}"
            )
        if period not in PERIOD_FORMATS.keys():
            raise TypeError("`period` should be one of `month`, `day`")

        params = {
            "type": period,
            "start": start.strftime(PERIOD_FORMATS[period]),
            "end": end.strftime(PERIOD_FORMATS[period]),
        }
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="hvac-history",
            params=params,
        )
        return cast(
            models.KamereonVehicleHvacHistoryData,
            response.get_attributes(schemas.KamereonVehicleHvacHistoryDataSchema),
        )

    async def get_hvac_sessions(
        self, start: datetime, end: datetime
    ) -> models.KamereonVehicleHvacSessionsData:
        """Get vehicle hvac sessions."""
        if not isinstance(start, datetime):
            raise TypeError(
                "`start` should be an instance of datetime.datetime, "
                f"not {start.__class__}"
            )
        if not isinstance(end, datetime):
            raise TypeError(
                f"`end` should be an instance of datetime.datetime, not {end.__class__}"
            )

        params = {
            "start": start.strftime(PERIOD_DAY_FORMAT),
            "end": end.strftime(PERIOD_DAY_FORMAT),
        }
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="hvac-sessions",
            params=params,
        )
        return cast(
            models.KamereonVehicleHvacSessionsData,
            response.get_attributes(schemas.KamereonVehicleHvacSessionsDataSchema),
        )

    async def set_ac_start(
        self, temperature: float, when: Optional[datetime] = None
    ) -> models.KamereonVehicleHvacStartActionData:
        """Start vehicle ac."""
        json: dict[str, Any] = {
            "data": {
                "type": "HvacStart",
                "attributes": {
                    "action": "start",
                    "targetTemperature": temperature,
                },
            }
        }

        if when:
            if not isinstance(when, datetime):
                raise TypeError(
                    "`when` should be an instance of datetime.datetime, "
                    f"not {when.__class__}"
                )
            start_date_time = when.astimezone(timezone.utc).strftime(PERIOD_TZ_FORMAT)
            json["data"]["attributes"]["startDateTime"] = start_date_time

        response = await self._set_vehicle_data("actions/hvac-start", json)
        return cast(
            models.KamereonVehicleHvacStartActionData,
            response.get_attributes(schemas.KamereonVehicleHvacStartActionDataSchema),
        )

    async def set_ac_stop(self) -> models.KamereonVehicleHvacStartActionData:
        """Stop vehicle ac."""
        json: dict[str, Any] = {
            "data": {
                "type": "HvacStart",
                "attributes": {
                    "action": "cancel",
                },
            }
        }

        response = await self._set_vehicle_data("actions/hvac-stop", json)
        return cast(
            models.KamereonVehicleHvacStartActionData,
            response.get_attributes(schemas.KamereonVehicleHvacStartActionDataSchema),
        )

    async def set_hvac_schedules(
        self, schedules: list[models.HvacSchedule]
    ) -> models.KamereonVehicleHvacScheduleActionData:
        """Set vehicle charge schedules."""
        for schedule in schedules:
            if not isinstance(schedule, models.HvacSchedule):
                raise TypeError(
                    "`schedules` should be a list of HvacSchedule, "
                    f"not {schedules.__class__}"
                )
        json: dict[str, Any] = {
            "data": {
                "type": "HvacSchedule",
                "attributes": {
                    "schedules": [schedule.for_json() for schedule in schedules]
                },
            }
        }

        response = await self._set_vehicle_data("actions/hvac-set-schedule", json)
        return cast(
            models.KamereonVehicleHvacScheduleActionData,
            response.get_attributes(
                schemas.KamereonVehicleHvacScheduleActionDataSchema
            ),
        )

    async def set_charge_schedules(
        self, schedules: list[models.ChargeSchedule]
    ) -> models.KamereonVehicleChargeScheduleActionData:
        """Set vehicle charge schedules."""
        for schedule in schedules:
            if not isinstance(schedule, models.ChargeSchedule):
                raise TypeError(
                    "`schedules` should be a list of ChargeSchedule, "
                    f"not {schedules.__class__}"
                )

        json: dict[str, Any] = {
            "data": {
                "type": "ChargeSchedule",
                "attributes": {
                    "schedules": [schedule.for_json() for schedule in schedules]
                },
            }
        }

        response = await self._set_vehicle_data("actions/charge-set-schedule", json)
        return cast(
            models.KamereonVehicleChargeScheduleActionData,
            response.get_attributes(
                schemas.KamereonVehicleChargeScheduleActionDataSchema
            ),
        )

    async def set_charge_mode(
        self, charge_mode: str
    ) -> models.KamereonVehicleChargeModeActionData:
        """Set vehicle charge mode."""
        json: dict[str, Any] = {
            "data": {
                "type": "ChargeMode",
                "attributes": {
                    "action": charge_mode,
                },
            }
        }

        response = await self._set_vehicle_data("actions/charge-set-mode", json)
        return cast(
            models.KamereonVehicleChargeModeActionData,
            response.get_attributes(schemas.KamereonVehicleChargeModeActionDataSchema),
        )

    async def set_charge_start(self) -> models.KamereonVehicleChargingStartActionData:
        """Start vehicle charge."""
        endpoint_definition = await self.get_endpoint_definition("actions/charge-start")
        json: dict[str, Any]
        if endpoint_definition.mode == "kcm":
            json = {
                "data": {
                    "type": "ChargePauseResume",
                    "attributes": {
                        "action": "resume",
                    },
                }
            }
        else:
            json = {
                "data": {
                    "type": "ChargingStart",
                    "attributes": {
                        "action": "start",
                    },
                }
            }
        response = await self._set_vehicle_data(endpoint_definition, json)
        return cast(
            models.KamereonVehicleChargingStartActionData,
            response.get_attributes(
                schemas.KamereonVehicleChargingStartActionDataSchema
            ),
        )

    async def set_charge_stop(self) -> models.KamereonVehicleChargingStartActionData:
        """Start vehicle charge."""
        endpoint_definition = await self.get_endpoint_definition("actions/charge-stop")
        json: dict[str, Any]
        if endpoint_definition.mode == "kcm":
            json = {
                "data": {
                    "type": "ChargePauseResume",
                    "attributes": {
                        "action": "pause",
                    },
                }
            }
        else:
            json = {
                "data": {
                    "type": "ChargingStart",
                    "attributes": {
                        "action": "stop",
                    },
                }
            }
        response = await self._set_vehicle_data(endpoint_definition, json)
        return cast(
            models.KamereonVehicleChargingStartActionData,
            response.get_attributes(
                schemas.KamereonVehicleChargingStartActionDataSchema
            ),
        )

    async def start_horn_lights(self, target: str):
        if target not in ["horn", "lights"]:
            raise ValueError("Target must be either 'horn' or 'lights'")

        endpoint_definition = await self.get_endpoint_definition(
            f"actions/{target}-start"
        )
        json: dict[str, Any] = {
            "data": {
                "type": "HornLights",
                "attributes": {"action": "start", "target": target},
            }
        }
        response = await self._set_vehicle_data(endpoint_definition, json)
        return response

    async def start_horn(self) -> dict[str, Any]:
        json: dict[str, Any] = {
            "data": {
                "type": "HornLights",
                "attributes": {"action": "start", "target": "horn"},
            }
        }
        response = await self._set_vehicle_data("actions/horn-start", json)
        return response.raw_data

    async def start_lights(self) -> dict[str, Any]:
        ```suggestion
        json: dict[str, Any] = {
            "data": {
                "type": "HornLights",
                "attributes": {"action": "start", "target": "lights"},
            }
        }
        response = await self._set_vehicle_data("actions/lights-start", json)
        return response.raw_data

    async def supports_endpoint(self, endpoint: str) -> bool:
        """Check if vehicle supports endpoint."""
        details = await self.get_details()
        return details.supports_endpoint(endpoint)
