"""Tests for Kamereon models."""
from typing import cast

import pytest
from tests import fixtures

from renault_api.kamereon import models
from renault_api.kamereon import schemas


@pytest.mark.parametrize(
    "filename",
    fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_action"),
)
def test_vehicle_action_response(filename: str) -> None:
    """Test vehicle action response."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehicleDataResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the guid is hidden
    assert response.data is not None
    assert response.data.id == "guid"


def test_vehicle_action_response_attributes() -> None:
    """Test vehicle action response attributes."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_action/hvac-start.start.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    assert response.data is not None
    assert response.data.raw_data["attributes"] == {
        "action": "start",
        "targetTemperature": 21.0,
    }


def test_charge_schedule_for_json() -> None:
    """Test for updating charge settings."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/charging-settings.multi.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    vehicle_data = cast(
        models.KamereonVehicleChargingSettingsData,
        response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
    )

    # Check that for_json returns the same as the original data
    assert vehicle_data.schedules is not None
    for_json = {
        "schedules": list(schedule.for_json() for schedule in vehicle_data.schedules)
    }
    assert for_json == {
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": {"startTime": "T00:00Z", "duration": 450},
                "tuesday": {"startTime": "T00:00Z", "duration": 450},
                "wednesday": {"startTime": "T00:00Z", "duration": 450},
                "thursday": {"startTime": "T00:00Z", "duration": 450},
                "friday": {"startTime": "T00:00Z", "duration": 450},
                "saturday": {"startTime": "T00:00Z", "duration": 450},
                "sunday": {"startTime": "T00:00Z", "duration": 450},
            },
            {
                "id": 2,
                "activated": True,
                "monday": {"startTime": "T23:30Z", "duration": 15},
                "tuesday": {"startTime": "T23:30Z", "duration": 15},
                "wednesday": {"startTime": "T23:30Z", "duration": 15},
                "thursday": {"startTime": "T23:30Z", "duration": 15},
                "friday": {"startTime": "T23:30Z", "duration": 15},
                "saturday": {"startTime": "T23:30Z", "duration": 15},
                "sunday": {"startTime": "T23:30Z", "duration": 15},
            },
            {
                "id": 3,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            },
            {
                "id": 4,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            },
            {
                "id": 5,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            },
        ]
    }

    # Test update specific day
    vehicle_data.update(
        {
            "id": 1,
            "tuesday": {"startTime": "T12:00Z", "duration": 15},
        }
    )
    assert vehicle_data.schedules[0].tuesday is not None
    assert vehicle_data.schedules[0].tuesday.startTime == "T12:00Z"
    assert vehicle_data.schedules[0].tuesday.duration == 15

    # Test update activated state
    assert vehicle_data.schedules[1].activated
    vehicle_data.update(
        {
            "id": 2,
            "activated": False,
        }
    )
    assert not vehicle_data.schedules[1].activated

    # Activated flag has been updated in 'vehicle_data.update'
    # Refresh for_json with the updated data
    for_json = {  # type: ignore[unreachable]
        "schedules": list(schedule.for_json() for schedule in vehicle_data.schedules)
    }
    assert for_json == {
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": {"startTime": "T00:00Z", "duration": 450},
                "tuesday": {"startTime": "T12:00Z", "duration": 15},
                "wednesday": {"startTime": "T00:00Z", "duration": 450},
                "thursday": {"startTime": "T00:00Z", "duration": 450},
                "friday": {"startTime": "T00:00Z", "duration": 450},
                "saturday": {"startTime": "T00:00Z", "duration": 450},
                "sunday": {"startTime": "T00:00Z", "duration": 450},
            },
            {
                "id": 2,
                "activated": False,
                "monday": {"startTime": "T23:30Z", "duration": 15},
                "tuesday": {"startTime": "T23:30Z", "duration": 15},
                "wednesday": {"startTime": "T23:30Z", "duration": 15},
                "thursday": {"startTime": "T23:30Z", "duration": 15},
                "friday": {"startTime": "T23:30Z", "duration": 15},
                "saturday": {"startTime": "T23:30Z", "duration": 15},
                "sunday": {"startTime": "T23:30Z", "duration": 15},
            },
            {
                "id": 3,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            },
            {
                "id": 4,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            },
            {
                "id": 5,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            },
        ]
    }


def test_hvac_schedule_for_json() -> None:
    """Test for parsing and serializing settings."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_data/hvac-settings.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    vehicle_data = cast(
        models.KamereonVehicleHvacSettingsData,
        response.get_attributes(schemas.KamereonVehicleHvacSettingsDataSchema),
    )

    # verify for_json returns proper original data
    assert vehicle_data.schedules is not None
    for_json = {
        "schedules": list(schedule.for_json() for schedule in vehicle_data.schedules)
    }
    expected_json = {
        "schedules": [
            {
                "id": 1,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            },
            {
                "id": 2,
                "activated": True,
                "monday": None,
                "tuesday": None,
                "wednesday": {"readyAtTime": "T15:15Z"},
                "thursday": None,
                "friday": {"readyAtTime": "T15:15Z"},
                "saturday": None,
                "sunday": None,
            },
        ]
    }
    for i in [3, 4, 5]:
        expected_json["schedules"].append(
            {
                "id": i,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            }
        )
    assert for_json == expected_json

    # perform an update
    vehicle_data.schedules[0].activated = True
    vehicle_data.schedules[0].sunday = models.HvacDaySchedule(
        raw_data={}, readyAtTime="T20:30Z"
    )

    for_json = {
        "schedules": list(schedule.for_json() for schedule in vehicle_data.schedules)
    }
    expected_json = {
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": {"readyAtTime": "T20:30Z"},
            },
            {
                "id": 2,
                "activated": True,
                "monday": None,
                "tuesday": None,
                "wednesday": {"readyAtTime": "T15:15Z"},
                "thursday": None,
                "friday": {"readyAtTime": "T15:15Z"},
                "saturday": None,
                "sunday": None,
            },
        ]
    }
    for i in [3, 4, 5]:
        expected_json["schedules"].append(
            {
                "id": i,
                "activated": False,
                "monday": None,
                "tuesday": None,
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": None,
            }
        )

    assert for_json == expected_json
