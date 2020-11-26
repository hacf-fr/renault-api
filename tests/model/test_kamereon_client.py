"""Tests for Kamereon models."""
from tests import get_response_content

from renault_api.model import kamereon as model


FIXTURE_PATH = "tests/fixtures/kamereon"


def test_person_response() -> None:
    """Test person details response."""
    response: model.KamereonPersonResponse = get_response_content(
        f"{FIXTURE_PATH}/person.json", model.KamereonPersonResponseSchema
    )
    response.raise_for_error_code()
    assert response.accounts[0].accountId == "account-id-1"
    assert response.accounts[0].accountType == "MYRENAULT"
    assert response.accounts[0].accountStatus == "ACTIVE"

    assert response.accounts[1].accountId == "account-id-2"
    assert response.accounts[1].accountType == "SFDC"
    assert response.accounts[1].accountStatus == "ACTIVE"
