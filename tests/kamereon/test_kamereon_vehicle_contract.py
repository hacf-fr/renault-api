"""Tests for Kamereon models."""

import pytest

from tests import fixtures

from renault_api.kamereon import has_required_contracts
from renault_api.kamereon import models
from renault_api.kamereon import schemas


@pytest.mark.parametrize(
    "filename",
    fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_contract"),
)
def test_vehicle_contract_response(filename: str) -> None:
    """Test vehicle contract response."""
    response: models.KamereonVehicleContractsResponse = (
        fixtures.get_file_content_as_wrapped_schema(
            filename, schemas.KamereonVehicleContractsResponseSchema, "contractList"
        )
    )
    response.raise_for_error_code()
    assert response.contractList is not None
    for contract in response.contractList:
        if contract.contractId:
            assert contract.contractId.startswith(
                "AB1234"
            ), "Ensure contractId is obfuscated."


def test_has_required_contract_1() -> None:
    """Test has_required_contract."""
    response: models.KamereonVehicleContractsResponse = (
        fixtures.get_file_content_as_wrapped_schema(
            f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_contract/fr_FR.1.json",
            schemas.KamereonVehicleContractsResponseSchema,
            "contractList",
        )
    )
    response.raise_for_error_code()
    assert response.contractList is not None

    assert has_required_contracts(response.contractList, "battery-status")
    # "Deprecated in 0.1.3, contract codes are country-specific"
    # " and can't be used to guess requirements."
    # assert not has_required_contracts(response.contractList, "charge-mode")
    # assert not has_required_contracts(response.contractList, "charging-settings")
    # assert not has_required_contracts(response.contractList, "hvac-history")
    # assert not has_required_contracts(response.contractList, "hvac-sessions")
    # assert not has_required_contracts(response.contractList, "hvac-status")


def test_has_required_contract_2() -> None:
    """Test has_required_contract."""
    response: models.KamereonVehicleContractsResponse = (
        fixtures.get_file_content_as_wrapped_schema(
            f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_contract/fr_FR.2.json",
            schemas.KamereonVehicleContractsResponseSchema,
            "contractList",
        )
    )
    response.raise_for_error_code()
    assert response.contractList is not None

    assert has_required_contracts(response.contractList, "battery-status")
    assert has_required_contracts(response.contractList, "charge-mode")
    assert has_required_contracts(response.contractList, "charging-settings")
    assert has_required_contracts(response.contractList, "hvac-history")
    assert has_required_contracts(response.contractList, "hvac-sessions")
    assert has_required_contracts(response.contractList, "hvac-status")
