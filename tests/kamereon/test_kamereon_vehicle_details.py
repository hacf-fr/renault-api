"""Tests for Kamereon models."""
import os

import pytest
from tests import fixtures

from renault_api.kamereon import models
from renault_api.kamereon import schemas

EXPECTED_SPECS = {
    "captur_ii.1.json": {
        "get_brand_label": "RENAULT",
        "get_energy_code": "ESS",
        "get_model_code": "XJB1SU",
        "get_model_label": "CAPTUR II",
        "reports_charging_power_in_watts": False,
        "uses_electricity": False,
        "uses_fuel": True,
        "supports-hvac-status": False,
        "supports-location": True,
    },
    "captur_ii.2.json": {
        "get_brand_label": "RENAULT",
        "get_energy_code": "ESS",
        "get_model_code": "XJB1SU",
        "get_model_label": "CAPTUR II",
        "reports_charging_power_in_watts": False,
        "uses_electricity": True,
        "uses_fuel": True,
        "supports-hvac-status": False,
        "supports-location": True,
    },
    "duster.1.json": {
        "get_brand_label": "RENAULT",
        "get_energy_code": "ESS",
        "get_model_code": "XJD1SU",
        "get_model_label": "NEW DUSTER",
        "reports_charging_power_in_watts": False,
        "uses_electricity": False,
        "uses_fuel": True,
        "supports-hvac-status": True,
        "supports-location": True,
    },
    "twingo_ze.1.json": {
        "get_brand_label": "RENAULT",
        "get_energy_code": "ELEC",
        "get_model_code": "X071VE",
        "get_model_label": "TWINGO III",
        "reports_charging_power_in_watts": False,
        "uses_electricity": True,
        "uses_fuel": False,
        "supports-hvac-status": False,
        "supports-location": True,
    },
    "zoe_40.1.json": {
        "get_brand_label": "RENAULT",
        "get_energy_code": "ELEC",
        "get_model_code": "X101VE",
        "get_model_label": "ZOE",
        "reports_charging_power_in_watts": True,
        "uses_electricity": True,
        "uses_fuel": False,
        "supports-hvac-status": True,
        "supports-location": False,
    },
    "zoe_40.2.json": {
        "get_brand_label": "RENAULT",
        "get_energy_code": "ELEC",
        "get_model_code": "X101VE",
        "get_model_label": "ZOE",
        "reports_charging_power_in_watts": True,
        "uses_electricity": True,
        "uses_fuel": False,
        "supports-hvac-status": True,
        "supports-location": False,
    },
    "zoe_50.1.json": {
        "get_brand_label": "RENAULT",
        "get_energy_code": "ELEC",
        "get_model_code": "X102VE",
        "get_model_label": "ZOE",
        "reports_charging_power_in_watts": False,
        "uses_electricity": True,
        "uses_fuel": False,
        "supports-hvac-status": True,
        "supports-location": True,
    },
    "spring.1.json": {
        "get_brand_label": "DACIA",
        "get_energy_code": "ELEC",
        "get_model_code": "XBG1VE",
        "get_model_label": "SPRING",
        "reports_charging_power_in_watts": False,
        "uses_electricity": True,
        "uses_fuel": False,
        "supports-hvac-status": True,
        "supports-location": True,
    },
}


@pytest.mark.parametrize(
    "filename",
    fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_details"),
)
def test_vehicles_response(filename: str) -> None:
    """Test vehicles list response."""
    response: models.KamereonVehiclesResponse = fixtures.get_file_content_as_schema(
        filename, schemas.KamereonVehiclesResponseSchema
    )
    response.raise_for_error_code()
    # Ensure the account id is hidden
    assert response.accountId is not None
    assert response.accountId.startswith("account-id")
    assert response.vehicleLinks is not None
    for vehicle_link in response.vehicleLinks:
        # Ensure the VIN and RegistrationNumber are hidden
        assert vehicle_link.vin
        assert vehicle_link.vin.startswith(
            ("VF1AAAA", "UU1AAAA")
        ), "Ensure vin is obfuscated."

        vehicle_details = vehicle_link.vehicleDetails
        assert vehicle_details
        assert vehicle_details.vin
        assert vehicle_details.vin.startswith(
            ("VF1AAAA", "UU1AAAA")
        ), "Ensure vin is obfuscated."
        assert vehicle_details.registrationNumber
        assert vehicle_details.registrationNumber.startswith(
            "REG-"
        ), "Ensure registrationNumber is obfuscated."
        assert vehicle_details.radioCode == "1234", "Ensure radioCode is obfuscated."
        if os.path.basename(filename) in EXPECTED_SPECS:
            generated_specs = {
                "get_brand_label": vehicle_details.get_brand_label(),
                "get_energy_code": vehicle_details.get_energy_code(),
                "get_model_code": vehicle_details.get_model_code(),
                "get_model_label": vehicle_details.get_model_label(),
                "reports_charging_power_in_watts": vehicle_details.reports_charging_power_in_watts(),  # noqa: B950
                "uses_electricity": vehicle_details.uses_electricity(),
                "uses_fuel": vehicle_details.uses_fuel(),
                "supports-hvac-status": vehicle_details.supports_endpoint(
                    "hvac-status"
                ),
                "supports-location": vehicle_details.supports_endpoint("location"),
            }
            assert EXPECTED_SPECS[os.path.basename(filename)] == generated_specs
