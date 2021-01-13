"""Tests for Kamereon models."""
import pytest
from tests import fixtures

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
