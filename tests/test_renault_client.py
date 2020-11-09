"""Test cases for the Renault client API keys."""
import pytest
import responses  # type: ignore
from pyze.api.credentials import BasicCredentialStore  # type: ignore
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.fixtures import gigya_responses
from tests.fixtures import kamereon_responses
from tests.test_credential_store import get_credential_store

from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.const import CONF_LOCALE
from renault_api.renault_client import RenaultClient


def get_renault_client() -> RenaultClient:
    """Build RenaultClient for testing."""
    renault_client = RenaultClient(credential_store=get_credential_store())
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            json=gigya_responses.MOCK_LOGIN,
        )
        mocked_responses.add(
            responses.POST,
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            json=gigya_responses.MOCK_GETACCOUNTINFO,
        )
        mocked_responses.add(
            responses.POST,
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            json=gigya_responses.MOCK_GETJWT,
        )
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/persons/{TEST_PERSON_ID}?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_PERSONS,
        )

        renault_client.login(TEST_USERNAME, TEST_PASSWORD)
        renault_client.get_accounts()  # trigger getJWT
    return renault_client


def test_missing_locale() -> None:
    """Ensure client can be initialised."""
    credential_store: BasicCredentialStore = BasicCredentialStore()
    for key in [
        CONF_LOCALE,
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        with pytest.raises(KeyError):
            RenaultClient(credential_store=credential_store)
        credential_store.store(key, "not-empty", None)

    # succeeds
    RenaultClient(credential_store=credential_store)


def test_get_accounts() -> None:
    """Test client get_accounts."""
    renault_client = RenaultClient(credential_store=get_credential_store())
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_GIGYA_URL}/accounts.login",
            status=200,
            json=gigya_responses.MOCK_LOGIN,
        )
        mocked_responses.add(
            responses.POST,
            f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
            status=200,
            json=gigya_responses.MOCK_GETACCOUNTINFO,
        )

        assert "gigya-person-id" not in renault_client._credential_store
        renault_client.login(TEST_USERNAME, TEST_PASSWORD)
        assert len(mocked_responses.calls) == 2
        assert (
            mocked_responses.calls[0].request.url == TEST_GIGYA_URL + "/accounts.login"
        )
        assert (
            mocked_responses.calls[1].request.url
            == TEST_GIGYA_URL + "/accounts.getAccountInfo"
        )
        assert "gigya-person-id" in renault_client._credential_store
        assert renault_client._credential_store["gigya-person-id"] == TEST_PERSON_ID

    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.POST,
            f"{TEST_GIGYA_URL}/accounts.getJWT",
            status=200,
            json=gigya_responses.MOCK_GETJWT,
        )
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/persons/{TEST_PERSON_ID}?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_PERSONS,
        )
        accounts = renault_client.get_accounts()
        assert len(accounts) == 2

        account_id = accounts[0]["accountId"]
        assert account_id == TEST_ACCOUNT_ID
