"""Tests for Kamereon models."""
from tests import fixtures

from renault_api.kamereon import models
from renault_api.kamereon import schemas


def test_person_response() -> None:
    """Test person details response."""
    response: models.KamereonPersonResponse = fixtures.get_file_content_as_schema(
        f"{fixtures.KAMEREON_FIXTURE_PATH}/person.json",
        schemas.KamereonPersonResponseSchema,
    )
    response.raise_for_error_code()
    assert response.accounts[0].accountId == "account-id-1"
    assert response.accounts[0].accountType == "MYRENAULT"
    assert response.accounts[0].accountStatus == "ACTIVE"

    assert response.accounts[1].accountId == "account-id-2"
    assert response.accounts[1].accountType == "SFDC"
    assert response.accounts[1].accountStatus == "ACTIVE"

    for account in response.accounts:
        assert account.accountId
        assert account.accountId.startswith("account-id")
