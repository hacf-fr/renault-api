"""Client for Renault API."""
import logging
from datetime import datetime
from typing import cast

from .kamereon import Kamereon
from .model import kamereon as model


_LOGGER = logging.getLogger(__name__)

PERIOD_DAY_FORMAT = "%Y%m%d"
PERIOD_MONTH_FORMAT = "%Y%m"
PERIOD_FORMATS = {"day": PERIOD_DAY_FORMAT, "month": PERIOD_MONTH_FORMAT}


class RenaultVehicle:
    """Proxy to a Renault vehicle."""

    def __init__(
        self,
        kamereon: Kamereon,
        account_id: str,
        vin: str,
    ) -> None:
        """Initialise Renault account."""
        self._kamereon = kamereon
        self._account_id = account_id
        self._vin = vin

    async def get_battery_status(self) -> model.KamereonVehicleBatteryStatusData:
        """Get vehicle battery status."""
        response = await self._kamereon.get_vehicle_battery_status(
            self._account_id, self._vin
        )
        return cast(
            model.KamereonVehicleBatteryStatusData,
            response.get_attributes(model.KamereonVehicleBatteryStatusDataSchema),
        )

    async def get_location(self) -> model.KamereonVehicleLocationData:
        """Get vehicle location."""
        response = await self._kamereon.get_vehicle_location(
            self._account_id, self._vin
        )
        return cast(
            model.KamereonVehicleLocationData,
            response.get_attributes(model.KamereonVehicleLocationDataSchema),
        )

    async def get_hvac_status(self) -> model.KamereonVehicleHvacStatusData:
        """Get vehicle hvac status."""
        response = await self._kamereon.get_vehicle_hvac_status(
            self._account_id, self._vin
        )
        return cast(
            model.KamereonVehicleHvacStatusData,
            response.get_attributes(model.KamereonVehicleHvacStatusDataSchema),
        )

    async def get_charge_mode(self) -> model.KamereonVehicleChargeModeData:
        """Get vehicle charge mode."""
        response = await self._kamereon.get_vehicle_charge_mode(
            self._account_id, self._vin
        )
        return cast(
            model.KamereonVehicleChargeModeData,
            response.get_attributes(model.KamereonVehicleChargeModeDataSchema),
        )

    async def get_cockpit(self) -> model.KamereonVehicleCockpitData:
        """Get vehicle cockpit."""
        response = await self._kamereon.get_vehicle_cockpit(self._account_id, self._vin)
        return cast(
            model.KamereonVehicleCockpitData,
            response.get_attributes(model.KamereonVehicleCockpitDataSchema),
        )

    async def get_lock_status(self) -> model.KamereonVehicleLockStatusData:
        """Get vehicle lock status."""
        response = await self._kamereon.get_vehicle_lock_status(
            self._account_id, self._vin
        )
        return cast(
            model.KamereonVehicleLockStatusData,
            response.get_attributes(model.KamereonVehicleLockStatusDataSchema),
        )

    async def get_charging_settings(self) -> model.KamereonVehicleChargingSettingsData:
        """Get vehicle charging settings."""
        response = await self._kamereon.get_vehicle_charging_settings(
            self._account_id, self._vin
        )
        return cast(
            model.KamereonVehicleChargingSettingsData,
            response.get_attributes(model.KamereonVehicleChargingSettingsDataSchema),
        )

    async def get_notification_settings(
        self,
    ) -> model.KamereonVehicleNotificationSettingsData:
        """Get vehicle notification settings."""
        response = await self._kamereon.get_vehicle_notification_settings(
            self._account_id, self._vin
        )
        return cast(
            model.KamereonVehicleNotificationSettingsData,
            response.get_attributes(
                model.KamereonVehicleNotificationSettingsDataSchema
            ),
        )

    async def get_charge_history(
        self, start: datetime, end: datetime, period: str = "month"
    ) -> model.KamereonVehicleChargeHistoryData:
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
        response = await self._kamereon.get_vehicle_charge_history(
            self._account_id,
            self._vin,
            params=params,
        )
        return cast(
            model.KamereonVehicleChargeHistoryData,
            response.get_attributes(model.KamereonVehicleChargeHistoryDataSchema),
        )

    async def get_charges(
        self, start: datetime, end: datetime
    ) -> model.KamereonVehicleChargesData:
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
        response = await self._kamereon.get_vehicle_charges(
            self._account_id,
            self._vin,
            params=params,
        )
        return cast(
            model.KamereonVehicleChargesData,
            response.get_attributes(model.KamereonVehicleChargesDataSchema),
        )

    async def get_hvac_history(
        self, start: datetime, end: datetime, period: str = "month"
    ) -> model.KamereonVehicleHvacHistoryData:
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
        response = await self._kamereon.get_vehicle_hvac_history(
            self._account_id,
            self._vin,
            params=params,
        )
        return cast(
            model.KamereonVehicleHvacHistoryData,
            response.get_attributes(model.KamereonVehicleHvacHistoryDataSchema),
        )

    async def get_hvac_sessions(
        self, start: datetime, end: datetime
    ) -> model.KamereonVehicleHvacSessionsData:
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
        response = await self._kamereon.get_vehicle_hvac_sessions(
            self._account_id,
            self._vin,
            params=params,
        )
        return cast(
            model.KamereonVehicleHvacSessionsData,
            response.get_attributes(model.KamereonVehicleHvacSessionsDataSchema),
        )
