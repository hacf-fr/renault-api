"""Test cases for the Renault client API keys."""
import pytest
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from tests import get_file_content
from tests import get_jwt
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN

from renault_api.kamereon import CREDENTIAL_GIGYA_JWT
from renault_api.kamereon import CREDENTIAL_GIGYA_LOGIN_TOKEN
from renault_api.kamereon import CREDENTIAL_GIGYA_PERSON_ID
from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential
from renault_api.model.kamereon import ChargeState
from renault_api.model.kamereon import PlugState
from renault_api.renault_client import RenaultClient
from renault_api.renault_vehicle import RenaultVehicle

TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_KAMEREON_ACCOUNT_URL = f"{TEST_KAMEREON_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"
TEST_KAMEREON_VEHICLE_URL1 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
)
TEST_KAMEREON_VEHICLE_URL2 = (
    f"{TEST_KAMEREON_ACCOUNT_URL}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"
)
FIXTURE_PATH = "tests/fixtures/kamereon/"
QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
async def vehicle(websession: ClientSession) -> RenaultVehicle:
    """Fixture for testing Gigya."""
    client = RenaultClient(websession=websession, locale=TEST_LOCALE)
    client._kamereon._credentials[CREDENTIAL_GIGYA_LOGIN_TOKEN] = Credential(
        "sample-cookie-value"
    )
    client._kamereon._credentials[CREDENTIAL_GIGYA_PERSON_ID] = Credential(
        TEST_PERSON_ID
    )
    client._kamereon._credentials[CREDENTIAL_GIGYA_JWT] = JWTCredential(get_jwt())
    account = await client.get_api_account(TEST_ACCOUNT_ID)
    return await account.get_api_vehicle(TEST_VIN)


@pytest.mark.asyncio
async def test_get_battery_status(vehicle: RenaultVehicle) -> None:
    """Test get_battery_status."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL2}/battery-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/battery-status.1.json"),
        )
        battery_status_data = await vehicle.get_battery_status()

        assert battery_status_data.timestamp == "2020-11-17T09:06:48+01:00"
        assert battery_status_data.batteryLevel == 50
        assert battery_status_data.batteryAutonomy == 128
        assert battery_status_data.batteryCapacity == 0
        assert battery_status_data.batteryAvailableEnergy == 0
        assert battery_status_data.plugStatus == 0
        assert battery_status_data.chargingStatus == -1.0
        assert battery_status_data.get_plug_status() == PlugState.UNPLUGGED
        assert battery_status_data.get_charging_status() == ChargeState.CHARGE_ERROR


@pytest.mark.asyncio
async def test_get_hvac_status(vehicle: RenaultVehicle) -> None:
    """Test get_hvac_status."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_KAMEREON_VEHICLE_URL1}/hvac-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/hvac-status.json"),
        )
        battery_status_data = await vehicle.get_hvac_status()

        assert battery_status_data.externalTemperature == 8.0
        assert battery_status_data.hvacStatus == "off"
