"""Tests for Kamereon models."""
from typing import cast

from tests import fixtures

from renault_api.kamereon import models
from renault_api.kamereon import schemas


FIXTURE_PATH = "tests/fixtures/kamereon/vehicle_data"

TEST_UPDATE = {
    "id": 1,
    "tuesday": {"startTime": "T12:00Z", "duration": 15},
}


def test_for_json() -> None:
    """Test for updating charge settings."""
    response: models.KamereonVehicleDataResponse = fixtures.get_file_content_as_schema(
        f"{FIXTURE_PATH}/charging-settings.json",
        schemas.KamereonVehicleDataResponseSchema,
    )
    response.raise_for_error_code()
    vehicle_data = cast(
        models.KamereonVehicleChargingSettingsData,
        response.get_attributes(schemas.KamereonVehicleChargingSettingsDataSchema),
    )

    # Check that for_json returns the same as the original data
    for_json = {
        "schedules": list(schedule.for_json() for schedule in vehicle_data.schedules)
    }
    assert for_json == {
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": {"startTime": "T12:00Z", "duration": 15},
                "tuesday": {"startTime": "T04:30Z", "duration": 420},
                "wednesday": {"startTime": "T22:30Z", "duration": 420},
                "thursday": {"startTime": "T22:00Z", "duration": 420},
                "friday": {"startTime": "T12:15Z", "duration": 15},
                "saturday": {"startTime": "T12:30Z", "duration": 30},
                "sunday": {"startTime": "T12:45Z", "duration": 45},
            }
        ]
    }

    # Check that for_json returns the same as the original data
    for_json = {
        "schedules": list(schedule.for_json() for schedule in vehicle_data.schedules)
    }
    assert for_json == {
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": {"startTime": "T12:00Z", "duration": 15},
                "tuesday": {"startTime": "T04:30Z", "duration": 420},
                "wednesday": {"startTime": "T22:30Z", "duration": 420},
                "thursday": {"startTime": "T22:00Z", "duration": 420},
                "friday": {"startTime": "T12:15Z", "duration": 15},
                "saturday": {"startTime": "T12:30Z", "duration": 30},
                "sunday": {"startTime": "T12:45Z", "duration": 45},
            }
        ]
    }

    vehicle_data.update(TEST_UPDATE)
    assert vehicle_data.schedules[0].tuesday.startTime == "T12:00Z"
    assert vehicle_data.schedules[0].tuesday.duration == 15

    for_json = {
        "schedules": list(schedule.for_json() for schedule in vehicle_data.schedules)
    }
    assert for_json == {
        "schedules": [
            {
                "id": 1,
                "activated": True,
                "monday": {"startTime": "T12:00Z", "duration": 15},
                "tuesday": {"startTime": "T12:00Z", "duration": 15},
                "wednesday": {"startTime": "T22:30Z", "duration": 420},
                "thursday": {"startTime": "T22:00Z", "duration": 420},
                "friday": {"startTime": "T12:15Z", "duration": 15},
                "saturday": {"startTime": "T12:30Z", "duration": 30},
                "sunday": {"startTime": "T12:45Z", "duration": 45},
            }
        ]
    }
