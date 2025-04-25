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
        "schedules": [schedule.for_json() for schedule in vehicle_data.schedules]
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

    # Update days only
    vehicle_data.update(
        {
            "id": 1,
            "sunday": {"readyAtTime": "T20:30Z"},
            "tuesday": {"readyAtTime": "T20:30Z"},
            "thursday": None,
        }
    )

    for_json = {
        "schedules": [schedule.for_json() for schedule in vehicle_data.schedules]
    }
    expected_json = {
        "schedules": [
            {
                "id": 1,
                "activated": False,
                "monday": None,
                "tuesday": {"readyAtTime": "T20:30Z"},
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

    # Update 'activated' only
    vehicle_data.update(
        {
            "id": 2,
            "activated": False,
        }
    )

    for_json = {
        "schedules": [schedule.for_json() for schedule in vehicle_data.schedules]
    }
    expected_json = {
        "schedules": [
            {
                "id": 1,
                "activated": False,
                "monday": None,
                "tuesday": {"readyAtTime": "T20:30Z"},
                "wednesday": None,
                "thursday": None,
                "friday": None,
                "saturday": None,
                "sunday": {"readyAtTime": "T20:30Z"},
            },
            {
                "id": 2,
                "activated": False,
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
