"""Client for Renault API."""

from datetime import datetime
from datetime import timezone
from typing import Any
from typing import Optional
from typing import cast
from warnings import warn

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

    async def _get_vehicle_response(self, endpoint: str) -> models.KamereonResponse:
        """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
        details = await self.get_details()
        full_endpoint = details.get_endpoint(endpoint)
        if full_endpoint is None:
            raise EndpointNotAvailableError(endpoint, details.get_model_code())

        full_endpoint = ACCOUNT_ENDPOINT_ROOT.replace(
            "{account_id}", self.account_id
        ) + full_endpoint.replace("{vin}", self.vin)

        return await self.session.http_request("GET", full_endpoint)

    async def _get_vehicle_data(self, endpoint: str) -> models.KamereonResponse:
        """GET to /v{endpoint_version}/cars/{vin}/{endpoint}."""
        response = await self._get_vehicle_response(endpoint)
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

    async def get_charging_settings(self) -> models.KamereonVehicleChargingSettingsData:
        """Get vehicle charging settings."""
        warn(
            "Method `get_charging_settings` is deprecated, "
            "please use `get_charge_settings`.",
            DeprecationWarning,
            stacklevel=2,
        )
        response = await self._get_vehicle_data("charging-settings")
        return cast(
            models.KamereonVehicleChargingSettingsData,
            response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
        )

    async def get_charge_settings(self) -> models.KamereonVehicleChargingSettingsData:
        """Get vehicle charging settings."""
        response = await self._get_vehicle_response("charging-settings")
        if "data" in response.raw_data and "attributes" in response.raw_data["data"]:
            return response.raw_data["data"]["attributes"]
        return response.raw_data

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
        attributes = {
            "action": "start",
            "targetTemperature": temperature,
        }

        if when:
            if not isinstance(when, datetime):
                raise TypeError(
                    "`when` should be an instance of datetime.datetime, "
                    f"not {when.__class__}"
                )
            start_date_time = when.astimezone(timezone.utc).strftime(PERIOD_TZ_FORMAT)
            attributes["startDateTime"] = start_date_time

        response = await self.session.set_vehicle_action(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="actions/hvac-start",
            attributes=attributes,
        )
        return cast(
            models.KamereonVehicleHvacStartActionData,
            response.get_attributes(schemas.KamereonVehicleHvacStartActionDataSchema),
        )

    async def set_ac_stop(self) -> models.KamereonVehicleHvacStartActionData:
        """Stop vehicle ac."""
        attributes = {"action": "cancel"}

        response = await self.session.set_vehicle_action(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="actions/hvac-start",
            attributes=attributes,
        )
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
        attributes = {"schedules": [schedule.for_json() for schedule in schedules]}

        response = await self.session.set_vehicle_action(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="actions/hvac-schedule",
            attributes=attributes,
        )
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
        attributes = {"schedules": [schedule.for_json() for schedule in schedules]}

        response = await self.session.set_vehicle_action(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="actions/charge-schedule",
            attributes=attributes,
        )
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
        attributes = {"action": charge_mode}

        response = await self.session.set_vehicle_action(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="actions/charge-mode",
            attributes=attributes,
        )
        return cast(
            models.KamereonVehicleChargeModeActionData,
            response.get_attributes(schemas.KamereonVehicleChargeModeActionDataSchema),
        )

    async def set_charge_start(self) -> models.KamereonVehicleChargingStartActionData:
        """Start vehicle charge."""
        details = await self.get_details()

        if details.controls_action_via_kcm("charge"):
            attributes = {"action": "resume"}
            response = await self.session.set_vehicle_action(
                account_id=self.account_id,
                vin=self.vin,
                endpoint="charge/pause-resume",
                attributes=attributes,
                adapter_type="kcm",
            )
        else:
            attributes = {"action": "start"}
            response = await self.session.set_vehicle_action(
                account_id=self.account_id,
                vin=self.vin,
                endpoint="actions/charging-start",
                attributes=attributes,
            )
        return cast(
            models.KamereonVehicleChargingStartActionData,
            response.get_attributes(
                schemas.KamereonVehicleChargingStartActionDataSchema
            ),
        )

    async def set_charge_stop(self) -> models.KamereonVehicleChargingStartActionData:
        """Start vehicle charge."""
        details = await self.get_details()

        if details.controls_action_via_kcm("charge"):
            attributes = {"action": "pause"}
            response = await self.session.set_vehicle_action(
                account_id=self.account_id,
                vin=self.vin,
                endpoint="charge/pause-resume",
                attributes=attributes,
                adapter_type="kcm",
            )
        else:
            attributes = {"action": "stop"}
            response = await self.session.set_vehicle_action(
                account_id=self.account_id,
                vin=self.vin,
                endpoint="actions/charging-start",
                attributes=attributes,
            )
        return cast(
            models.KamereonVehicleChargingStartActionData,
            response.get_attributes(
                schemas.KamereonVehicleChargingStartActionDataSchema
            ),
        )

    async def supports_endpoint(self, endpoint: str) -> bool:
        """Check if vehicle supports endpoint."""
        details = await self.get_details()
        return details.supports_endpoint(endpoint)
