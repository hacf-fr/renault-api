"""Client for Renault API."""
import logging
from datetime import datetime
from datetime import timezone
from typing import cast
from typing import List
from typing import Optional

from . import kamereon
from .kamereon import enums
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
        session: RenaultSession,
        account_id: str,
        vin: str,
    ) -> None:
        """Initialise Renault account."""
        self._session = session
        self._account_id = account_id
        self._vin = vin

    @property
    def session(self) -> RenaultSession:
        """Get session provider."""
        return self._session

    @property
    def account_id(self) -> str:
        """Get account id."""
        return self._account_id

    @property
    def vin(self) -> str:
        """Get vin."""
        return self._vin

    async def get_battery_status(self) -> models.KamereonVehicleBatteryStatusData:
        """Get vehicle battery status."""
        response = await kamereon.get_vehicle_battery_status_v2(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleBatteryStatusData,
            response.get_attributes(schemas.KamereonVehicleBatteryStatusDataSchema),
        )

    async def get_location(self) -> models.KamereonVehicleLocationData:
        """Get vehicle location."""
        response = await kamereon.get_vehicle_location(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleLocationData,
            response.get_attributes(schemas.KamereonVehicleLocationDataSchema),
        )

    async def get_hvac_status(self) -> models.KamereonVehicleHvacStatusData:
        """Get vehicle hvac status."""
        response = await kamereon.get_vehicle_hvac_status(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleHvacStatusData,
            response.get_attributes(schemas.KamereonVehicleHvacStatusDataSchema),
        )

    async def get_charge_mode(self) -> models.KamereonVehicleChargeModeData:
        """Get vehicle charge mode."""
        response = await kamereon.get_vehicle_charge_mode(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleChargeModeData,
            response.get_attributes(schemas.KamereonVehicleChargeModeDataSchema),
        )

    async def get_cockpit(self) -> models.KamereonVehicleCockpitData:
        """Get vehicle cockpit."""
        response = await kamereon.get_vehicle_cockpit(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleCockpitData,
            response.get_attributes(schemas.KamereonVehicleCockpitDataSchema),
        )

    async def get_lock_status(self) -> models.KamereonVehicleLockStatusData:
        """Get vehicle lock status."""
        response = await kamereon.get_vehicle_lock_status(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleLockStatusData,
            response.get_attributes(schemas.KamereonVehicleLockStatusDataSchema),
        )

    async def get_charging_settings(self) -> models.KamereonVehicleChargingSettingsData:
        """Get vehicle charging settings."""
        response = await kamereon.get_vehicle_charging_settings(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleChargingSettingsData,
            response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
        )

    async def get_notification_settings(
        self,
    ) -> models.KamereonVehicleNotificationSettingsData:
        """Get vehicle notification settings."""
        response = await kamereon.get_vehicle_notification_settings(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
        )
        return cast(
            models.KamereonVehicleNotificationSettingsData,
            response.get_attributes(
                schemas.KamereonVehicleNotificationSettingsDataSchema
            ),
        )

    async def get_charge_history(
        self, start: datetime, end: datetime, period: str = "month"
    ) -> models.KamereonVehicleChargeHistoryData:
        """Get vehicle charge history."""
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
        response = await kamereon.get_vehicle_charge_history(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            params=params,
        )
        return cast(
            models.KamereonVehicleChargeHistoryData,
            response.get_attributes(schemas.KamereonVehicleChargeHistoryDataSchema),
        )

    async def get_charges(
        self, start: datetime, end: datetime
    ) -> models.KamereonVehicleChargesData:
        """Get vehicle charge statistics."""
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
        response = await kamereon.get_vehicle_charges(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            params=params,
        )
        return cast(
            models.KamereonVehicleChargesData,
            response.get_attributes(schemas.KamereonVehicleChargesDataSchema),
        )

    async def get_hvac_history(
        self, start: datetime, end: datetime, period: str = "month"
    ) -> models.KamereonVehicleHvacHistoryData:
        """Get vehicle hvac history."""
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
        response = await kamereon.get_vehicle_hvac_history(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
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
        response = await kamereon.get_vehicle_hvac_sessions(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            params=params,
        )
        return cast(
            models.KamereonVehicleHvacSessionsData,
            response.get_attributes(schemas.KamereonVehicleHvacSessionsDataSchema),
        )

    async def set_ac_start(
        self, temperature: float, when: Optional[datetime] = None
    ) -> models.KamereonVehicleHvacStartActionData:
        """Start vehicle hvac."""
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

        response = await kamereon.set_vehicle_hvac_start(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            attributes=attributes,
        )
        return cast(
            models.KamereonVehicleHvacStartActionData,
            response.get_attributes(schemas.KamereonVehicleHvacStartActionDataSchema),
        )

    async def set_ac_stop(self) -> models.KamereonVehicleHvacStartActionData:
        """Stop vehicle hvac."""
        attributes = {"action": "cancel"}

        response = await kamereon.set_vehicle_hvac_start(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            attributes=attributes,
        )
        return cast(
            models.KamereonVehicleHvacStartActionData,
            response.get_attributes(schemas.KamereonVehicleHvacStartActionDataSchema),
        )

    async def set_charge_schedules(
        self, schedules: List[models.ChargeSchedule]
    ) -> models.KamereonVehicleChargeScheduleActionData:
        """Set vehicle charge schedules."""
        for schedule in schedules:
            if not isinstance(schedule, models.ChargeSchedule):  # pragma: no cover
                raise TypeError(
                    "`schedules` should be a list of ChargeSchedule, not {}".format(
                        schedules.__class__
                    )
                )
        attributes = {"schedules": list(schedule.for_json() for schedule in schedules)}

        response = await kamereon.set_vehicle_charge_schedule(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            attributes=attributes,
        )
        return cast(
            models.KamereonVehicleChargeScheduleActionData,
            response.get_attributes(
                schemas.KamereonVehicleChargeScheduleActionDataSchema
            ),
        )

    async def set_charge_mode(
        self, charge_mode: enums.ChargeMode
    ) -> models.KamereonVehicleChargeModeActionData:
        """Set vehicle charge mode."""
        if not isinstance(charge_mode, enums.ChargeMode):  # pragma: no cover
            raise TypeError(
                "`charge_mode` should be an instance of ChargeMode, not {}".format(
                    charge_mode.__class__
                )
            )
        attributes = {"action": charge_mode.name}

        response = await kamereon.set_vehicle_charge_mode(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            attributes=attributes,
        )
        return cast(
            models.KamereonVehicleChargeModeActionData,
            response.get_attributes(schemas.KamereonVehicleChargeModeActionDataSchema),
        )

    async def set_charge_start(self) -> models.KamereonVehicleChargingStartActionData:
        """Start vehicle charge."""
        attributes = {"action": "start"}

        response = await kamereon.set_vehicle_charging_start(
            self.session.websession,
            self.session.kamereon_root_url,
            self.session.kamereon_api_key,
            await self.session.get_jwt(),
            self.session.country,
            self._account_id,
            self._vin,
            attributes=attributes,
        )
        return cast(
            models.KamereonVehicleChargingStartActionData,
            response.get_attributes(
                schemas.KamereonVehicleChargingStartActionDataSchema
            ),
        )
