"""Tests for RenaultClient."""
from typing import Any
from typing import Type

from marshmallow.schema import Schema

from renault_api.model.kamereon import KamereonPersonResponse
from renault_api.model.kamereon import KamereonPersonResponseSchema
from renault_api.model.kamereon import KamereonVehiclesResponse
from renault_api.model.kamereon import KamereonVehiclesResponseSchema


def get_response_content(path: str, schema: Type[Schema]) -> Any:
    """Read fixture text file as string."""
    with open(f"tests/fixtures/kamereon/{path}", "r") as file:
        content = file.read()
    return schema.loads(content)


def test_person_response() -> None:
    """Test login response."""
    response: KamereonPersonResponse = get_response_content(
        "persons_detail.json", KamereonPersonResponseSchema
    )
    assert response.accounts[0].accountId == "account-id-1"
    assert response.accounts[0].accountType == "MYRENAULT"
    assert response.accounts[0].accountStatus == "ACTIVE"

    assert response.accounts[1].accountId == "account-id-2"
    assert response.accounts[1].accountType == "SFDC"
    assert response.accounts[1].accountStatus == "ACTIVE"


def test_vehicles_response() -> None:
    """Test login response."""
    response: KamereonVehiclesResponse = get_response_content(
        "account_vehicles.json", KamereonVehiclesResponseSchema
    )
    assert response.vehicleLinks[0].vin == "VF1AAAAA555777999"
