"""Tests for Kamereon models."""
from tests import get_response_content

from renault_api.kamereon import models
from renault_api.kamereon import schemas


FIXTURE_PATH = "tests/fixtures/kamereon"


def test_person_response() -> None:
    """Test person details response."""
    response: models.KamereonPersonResponse = get_response_content(
        f"{FIXTURE_PATH}/person.json", schemas.KamereonPersonResponseSchema
    )
    response.raise_for_error_code()
    assert response.accounts[0].accountId == "account-id-1"
    assert response.accounts[0].accountType == "MYRENAULT"
    assert response.accounts[0].accountStatus == "ACTIVE"

    assert response.accounts[1].accountId == "account-id-2"
    assert response.accounts[1].accountType == "SFDC"
    assert response.accounts[1].accountStatus == "ACTIVE"

    for account in response.accounts:
        assert account.get_account_id().startswith("account-id")
