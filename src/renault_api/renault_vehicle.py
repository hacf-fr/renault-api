"""Client for Renault API."""
import logging
from datetime import datetime
from typing import Any
from typing import Optional

from pyze.api import Kamereon  # type: ignore
from pyze.api.kamereon import Vehicle  # type: ignore
from pyze.api.schedule import ChargeMode  # type: ignore
from pyze.api.schedule import ChargeSchedules

_LOGGER = logging.getLogger(__package__)


class RenaultVehicle:
    """Proxy to a Renault vehicle."""

    def __init__(self, kamereon: Kamereon, vin: str) -> None:
        """Initialise Renault vehicle."""
        self._vehicle: Vehicle = Vehicle(vin, kamereon)

    def battery_status(self) -> Any:
        """Get vehicle battery status."""
        # GET 'battery-status'
        return self._vehicle.battery_status()

    def location(self) -> Any:
        """Get vehicle location."""
        # GET 'location'
        return self._vehicle.location()

    def hvac_status(self) -> Any:
        """Get vehicle hvac-status."""
        # GET 'hvac-status'
        return self._vehicle.hvac_status()

    def charge_mode(self) -> Any:
        """Get vehicle hvac-status."""
        # GET 'charge-mode'
        return self._vehicle.charge_mode()

    def mileage(self) -> Any:
        """Get vehicle cockpit data."""
        # GET 'cockpit'
        return self._vehicle.mileage()

    def lock_status(self) -> Any:
        """Get vehicle lock status."""
        # GET 'lock-status'
        return self._vehicle.lock_status()

    def charge_schedules(self) -> Any:
        """Get vehicle charge schedules."""
        # GET 'charging-settings'
        return self._vehicle.charge_schedules()

    def notification_settings(self) -> Any:
        """Get vehicle notification settings."""
        # GET 'notification-settings'
        return self._vehicle.notification_settings()

    def charge_history(self, start: datetime, end: datetime) -> Any:
        """Get vehicle charge history."""
        # GET 'charges'
        return self._vehicle.charge_history(start, end)

    def charge_statistics(
        self, start: datetime, end: datetime, period: str = "month"
    ) -> Any:
        """Get vehicle charge statistics."""
        # GET 'charge-history'
        return self._vehicle.charge_statistics(start, end, period)

    def hvac_history(self, start: datetime, end: datetime) -> Any:
        """Get vehicle hvac history."""
        # GET 'hvac-sessions'
        return self._vehicle.hvac_history(start, end)

    def hvac_statistics(
        self, start: datetime, end: datetime, period: str = "month"
    ) -> Any:
        """Get vehicle hvac statistics."""
        # GET 'hvac-history'
        return self._vehicle.hvac_statistics(start, end, period)

    def ac_start(self, when: Optional[datetime] = None, temperature: float = 21) -> Any:
        """Start vehicle charge."""
        # POST 'actions/hvac-start'
        return self._vehicle.ac_start(when, temperature)

    def cancel_ac(self) -> Any:
        """Start vehicle charge."""
        # POST 'actions/hvac-start'
        return self._vehicle.cancel_ac()

    def set_charge_schedules(self, schedules: ChargeSchedules) -> Any:
        """Start vehicle charge."""
        # POST 'actions/charge-schedule'
        return self._vehicle.set_charge_schedules(schedules)

    def set_charge_mode(self, charge_mode: ChargeMode) -> Any:
        """Set vehicle charge mode."""
        # POST 'actions/charge-mode'
        return self._vehicle.set_charge_mode(charge_mode)

    def charge_start(self) -> Any:
        """Start vehicle charge."""
        # POST 'actions/charging-start'
        return self._vehicle.charge_start()
