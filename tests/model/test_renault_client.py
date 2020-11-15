"""Tests for RenaultClient."""
from renault_api.model.renault_client import KamereonPersonResponse


def test_person_response() -> None:
    """Test login response."""
    mock_login_response = {
        "accounts": [
            {
                "accountId": "account-id-1",
                "accountType": "MYRENAULT",
                "accountStatus": "ACTIVE",
                "country": "FR",
                "personId": "person-id-1",
                "relationType": "OWNER",
            },
            {
                "accountId": "account-id-2",
                "externalId": "external-id-2",
                "accountType": "SFDC",
                "accountStatus": "ACTIVE",
                "country": "FR",
                "personId": "person-id-1",
                "relationType": "OWNER",
            },
        ]
    }
    response = KamereonPersonResponse(mock_login_response)
    assert response.accounts[0].account_id == "account-id-1"
    assert response.accounts[0].account_type == "MYRENAULT"
    assert response.accounts[0].account_status == "ACTIVE"

    assert response.accounts[1].account_id == "account-id-2"
    assert response.accounts[1].account_type == "SFDC"
    assert response.accounts[1].account_status == "ACTIVE"
