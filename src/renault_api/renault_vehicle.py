"""Client for Renault API."""
import logging
from datetime import datetime
from datetime import timezone
from typing import cast
from typing import Dict
from typing import List
from typing import Optional
from warnings import warn

import aiohttp

from .credential_store import CredentialStore
from .exceptions import RenaultException
from .kamereon import models
from .kamereon import schemas
from .renault_session import RenaultSession


_LOGGER = logging.getLogger(__name__)

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
        locale_details: Optional[Dict[str, str]] = None,
        credential_store: Optional[CredentialStore] = None,
        vehicle_details: Optional[models.KamereonVehicleDetails] = None,
        car_adapter: Optional[models.KamereonVehicleCarAdapterData] = None,
    ) -> None:
        """Initialise Renault vehicle."""
        self._account_id = account_id
        self._vin = vin
        self._vehicle_details = vehicle_details
        self._car_adapter = car_adapter
        self._contracts: Optional[List[models.KamereonVehicleContract]] = None

        if session:
            self._session = session
        else:
            if websession is None:  # pragma: no cover
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

    async def get_contracts(self) -> List[models.KamereonVehicleContract]:
        """Get vehicle contracts."""
        # await self.warn_on_method("get_contracts")
        if self._contracts:
            return self._contracts

        response = await self.session.get_vehicle_contracts(
            account_id=self.account_id,
            vin=self.vin,
        )
        if response.contractList is None:  # pragma: no cover
            raise ValueError("response.contractList is None")
        self._contracts = response.contractList
        return self._contracts

    async def get_battery_status(self) -> models.KamereonVehicleBatteryStatusData:
        """Get vehicle battery status."""
        # await self.warn_on_method("get_battery_status")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="battery-status",
        )
        return cast(
            models.KamereonVehicleBatteryStatusData,
            response.get_attributes(schemas.KamereonVehicleBatteryStatusDataSchema),
        )

    async def get_location(self) -> models.KamereonVehicleLocationData:
        """Get vehicle location."""
        # await self.warn_on_method("get_location")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="location",
        )
        return cast(
            models.KamereonVehicleLocationData,
            response.get_attributes(schemas.KamereonVehicleLocationDataSchema),
        )

    async def get_hvac_status(self) -> models.KamereonVehicleHvacStatusData:
        """Get vehicle hvac status."""
        # await self.warn_on_method("get_hvac_status")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="hvac-status",
        )
        return cast(
            models.KamereonVehicleHvacStatusData,
            response.get_attributes(schemas.KamereonVehicleHvacStatusDataSchema),
        )

    async def get_hvac_settings(self) -> models.KamereonVehicleHvacSettingsData:
        """Get vehicle hvac settings (schedule+mode)."""
        # await self.warn_on_method("get_hvac_settings")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="hvac-settings",
        )
        return cast(
            models.KamereonVehicleHvacSettingsData,
            response.get_attributes(schemas.KamereonVehicleHvacSettingsDataSchema),
        )

    async def get_charge_mode(self) -> models.KamereonVehicleChargeModeData:
        """Get vehicle charge mode."""
        # await self.warn_on_method("get_charge_mode")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="charge-mode",
        )
        return cast(
            models.KamereonVehicleChargeModeData,
            response.get_attributes(schemas.KamereonVehicleChargeModeDataSchema),
        )

    async def get_cockpit(self) -> models.KamereonVehicleCockpitData:
        """Get vehicle cockpit."""
        # await self.warn_on_method("get_cockpit")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="cockpit",
        )
        return cast(
            models.KamereonVehicleCockpitData,
            response.get_attributes(schemas.KamereonVehicleCockpitDataSchema),
        )

    async def get_lock_status(self) -> models.KamereonVehicleLockStatusData:
        """Get vehicle lock status."""
        # await self.warn_on_method("get_lock_status")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="lock-status",
        )
        return cast(
            models.KamereonVehicleLockStatusData,
            response.get_attributes(schemas.KamereonVehicleLockStatusDataSchema),
        )

    async def get_res_state(self) -> models.KamereonVehicleResStateData:
        """Get vehicle res state."""
        # await self.warn_on_method("get_res_state")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="res-state",
        )
        return cast(
            models.KamereonVehicleResStateData,
            response.get_attributes(schemas.KamereonVehicleResStateDataSchema),
        )

    async def get_charging_settings(self) -> models.KamereonVehicleChargingSettingsData:
        """Get vehicle charging settings."""
        # await self.warn_on_method("get_charging_settings")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="charging-settings",
        )
        return cast(
            models.KamereonVehicleChargingSettingsData,
            response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
        )

    async def get_notification_settings(
        self,
    ) -> models.KamereonVehicleNotificationSettingsData:
        """Get vehicle notification settings."""
        # await self.warn_on_method("get_notification_settings")
        response = await self.session.get_vehicle_data(
            account_id=self.account_id,
            vin=self.vin,
            endpoint="notification-settings",
        )
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
        # await self.warn_on_method("get_charge_history")
        if not isinstance(start, datetime):  # pragma: no cover
            raise TypeError(
                "`start` should be an instance of datetime.datetime, not {}".format(
                    start.__class__
                )
            )
        if not isinstance(end, datetime):  # pragma: no cover
            raise TypeError(
                "`end` should be an instance of datetime.datetime, not {}".format(
                    end.__class__
                )
            )
        if period not in PERIOD_FORMATS.keys():  # pragma: no cover
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
        # await self.warn_on_method("get_charges")
        if not isinstance(start, datetime):  # pragma: no cover
            raise TypeError(
                "`start` should be an instance of datetime.datetime, not {}".format(
                    start.__class__
                )
            )
        if not isinstance(end, datetime):  # pragma: no cover
            raise TypeError(
                "`end` should be an instance of datetime.datetime, not {}".format(
                    end.__class__
                )
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
        # await self.warn_on_method("get_hvac_history")
        if not isinstance(start, datetime):  # pragma: no cover
            raise TypeError(
                "`start` should be an instance of datetime.datetime, not {}".format(
                    start.__class__
                )
            )
        if not isinstance(end, datetime):  # pragma: no cover
            raise TypeError(
                "`end` should be an instance of datetime.datetime, not {}".format(
                    end.__class__
                )
            )
        if period not in PERIOD_FORMATS.keys():  # pragma: no cover
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
        # await self.warn_on_method("get_hvac_sessions")
        if not isinstance(start, datetime):  # pragma: no cover
            raise TypeError(
                "`start` should be an instance of datetime.datetime, not {}".format(
                    start.__class__
                )
            )
        if not isinstance(end, datetime):  # pragma: no cover
            raise TypeError(
                "`end` should be an instance of datetime.datetime, not {}".format(
                    end.__class__
                )
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
        # await self.warn_on_method("set_ac_start")
        attributes = {
            "action": "start",
            "targetTemperature": temperature,
        }

        if when:
            if not isinstance(when, datetime):  # pragma: no cover
                raise TypeError(
                    "`when` should be an instance of datetime.datetime, not {}".format(
                        when.__class__
                    )
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
        await self.warn_on_method("set_ac_stop")
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
        self, schedules: List[models.HvacSchedule]
    ) -> models.KamereonVehicleHvacScheduleActionData:
        """Set vehicle charge schedules."""
        # await self.warn_on_method("set_hvac_schedules")
        for schedule in schedules:
            if not isinstance(schedule, models.HvacSchedule):  # pragma: no cover
                raise TypeError(
                    "`schedules` should be a list of HvacSchedule, not {}".format(
                        schedules.__class__
                    )
                )
        attributes = {"schedules": list(schedule.for_json() for schedule in schedules)}

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
        self, schedules: List[models.ChargeSchedule]
    ) -> models.KamereonVehicleChargeScheduleActionData:
        """Set vehicle charge schedules."""
        # await self.warn_on_method("set_charge_schedules")
        for schedule in schedules:
            if not isinstance(schedule, models.ChargeSchedule):  # pragma: no cover
                raise TypeError(
                    "`schedules` should be a list of ChargeSchedule, not {}".format(
                        schedules.__class__
                    )
                )
        attributes = {"schedules": list(schedule.for_json() for schedule in schedules)}

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
        # await self.warn_on_method("set_charge_mode")
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
            response = response = await self.session.set_vehicle_action(
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
            response = response = await self.session.set_vehicle_action(
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

    async def has_contract_for_endpoint(self, endpoint: str) -> bool:
        """Check if vehicle has contract for endpoint."""
        # "Deprecated in 0.1.3, contract codes are country-specific"
        # " and can't be used to guess requirements."
        warn("This method is deprecated.", DeprecationWarning, stacklevel=2)
        return True  # pragma: no cover

    async def warn_on_method(self, method: str) -> None:
        """Log a warning if the method requires it."""
        details = await self.get_details()
        warning = details.warns_on_method(method)
        if warning:
            _LOGGER.warning(warning)
