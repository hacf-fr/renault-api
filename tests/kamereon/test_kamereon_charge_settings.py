"""Tests for Kamereon models."""
from typing import cast

import pytest
from tests import fixtures

from renault_api.kamereon import helpers
from renault_api.kamereon import models
from renault_api.kamereon import schemas
from renault_api.kamereon.exceptions import ModelValidationException


@pytest.fixture
def charge_settings() -> models.KamereonVehicleChargingSettingsData:
    """Test vehicle data for location.json."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/charging-settings.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()

    return cast(
        models.KamereonVehicleChargingSettingsData,
        response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
    )


def test_validation_success(
    charge_settings: models.KamereonVehicleChargingSettingsData,
) -> None:
    """Test validation of a good schedule list."""
    helpers.validate_charge_schedules(charge_settings.schedules)


def test_validation_invalid_start_time(
    charge_settings: models.KamereonVehicleChargingSettingsData,
) -> None:
    """Test validation of an invalid start time."""
    charge_settings.schedules[0].monday.startTime = "12:00"

    with pytest.raises(ModelValidationException) as excinfo:
        helpers.validate_charge_schedules(charge_settings.schedules)
    assert "is not a valid start time" in str(excinfo.value)


def test_validation_invalid_duration(
    charge_settings: models.KamereonVehicleChargingSettingsData,
) -> None:
    """Test validation of an invalid start time."""
    charge_settings.schedules[0].monday.startTime = "T12:00Z"
    charge_settings.schedules[0].monday.duration = 14
    with pytest.raises(ModelValidationException) as excinfo:
        helpers.validate_charge_schedules(charge_settings.schedules)
    assert "is not a valid duration" in str(excinfo.value)


def test_validation_overlap(
    charge_settings: models.KamereonVehicleChargingSettingsData,
) -> None:
    """Test validation of an overlap with the next day."""
    charge_settings.schedules[0].wednesday.startTime = "T22:30Z"
    charge_settings.schedules[0].wednesday.duration = 420
    charge_settings.schedules[0].thursday.startTime = "T01:00Z"
    with pytest.raises(ModelValidationException) as excinfo:
        helpers.validate_charge_schedules(charge_settings.schedules)
    assert "overlaps with next day schedule" in str(excinfo.value)
