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
    response: models.KameronVehicleContractsReponse = (
        fixtures.get_file_content_as_wrapped_schema(
            filename, schemas.KameronVehicleContractsReponseSchema, "contractList"
        )
    )
    response.raise_for_error_code()
    assert response.contractList
    for contract in response.contractList:
        if contract.contractId:
            assert contract.contractId.startswith(
                "AB1234"
            ), "Ensure contractId is obfuscated."


def test_has_required_contract_1() -> None:
    """Test has_required_contract."""
    response: models.KameronVehicleContractsReponse = (
        fixtures.get_file_content_as_wrapped_schema(
            f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_contract/fr_FR.1.json",
            schemas.KameronVehicleContractsReponseSchema,
            "contractList",
        )
    )
    response.raise_for_error_code()
    assert response.contractList

    assert has_required_contracts(response.contractList, "battery-status")
    assert not has_required_contracts(response.contractList, "charge-mode")
    assert not has_required_contracts(response.contractList, "charging-settings")
    assert not has_required_contracts(response.contractList, "hvac-history")
    assert not has_required_contracts(response.contractList, "hvac-sessions")
    assert not has_required_contracts(response.contractList, "hvac-status")


def test_has_required_contract_2() -> None:
    """Test has_required_contract."""
    response: models.KameronVehicleContractsReponse = (
        fixtures.get_file_content_as_wrapped_schema(
            f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicle_contract/fr_FR.2.json",
            schemas.KameronVehicleContractsReponseSchema,
            "contractList",
        )
    )
    response.raise_for_error_code()
    assert response.contractList

    assert has_required_contracts(response.contractList, "battery-status")
    assert has_required_contracts(response.contractList, "charge-mode")
    assert has_required_contracts(response.contractList, "charging-settings")
    assert has_required_contracts(response.contractList, "hvac-history")
    assert has_required_contracts(response.contractList, "hvac-sessions")
    assert has_required_contracts(response.contractList, "hvac-status")
