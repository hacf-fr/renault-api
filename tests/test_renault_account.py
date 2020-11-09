"""Test cases for the Renault client API keys."""
import responses  # type: ignore
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_VIN
from tests.fixtures import kamereon_responses
from tests.test_renault_client import get_renault_client

from renault_api.renault_account import RenaultAccount


def get_renault_account() -> RenaultAccount:
    """Build RenaultAccount for testing."""
    return get_renault_client().get_account(TEST_ACCOUNT_ID)


def test_get_vehicles() -> None:
    """Test account get_vehicles."""
    renault_account = get_renault_account()
    with responses.RequestsMock() as mocked_responses:
        mocked_responses.add(
            responses.GET,
            f"{TEST_KAMEREON_URL}/commerce/v1/accounts/{TEST_ACCOUNT_ID}/vehicles?country={TEST_COUNTRY}",  # noqa
            status=200,
            json=kamereon_responses.MOCK_ACCOUNTS_VEHICLES,
        )

        vehicles = renault_account.get_vehicles()
        assert "vehicleLinks" in vehicles
        vehicle_links = vehicles["vehicleLinks"]
        assert len(vehicle_links) == 1
        assert vehicle_links[0]["vin"] == TEST_VIN
