"""Test cases for retrieving information from the Kamereon client."""
import aiohttp
import pytest
from aioresponses import aioresponses
from tests import get_file_content
from tests import get_json_files
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN
from tests.test_kamereon_init import get_logged_in_kamereon

from renault_api.kamereon.client import KamereonClient

TEST_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
TEST_ACCOUNT_URL = f"{TEST_BASE_URL}/accounts/{TEST_ACCOUNT_ID}"
TEST_VEHICLE_URL1 = f"{TEST_ACCOUNT_URL}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
TEST_VEHICLE_URL2 = f"{TEST_ACCOUNT_URL}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"

FIXTURE_PATH = "tests/fixtures/kamereon/"

QUERY_STRING = f"country={TEST_COUNTRY}"


@pytest.fixture
def kamereon(websession: aiohttp.ClientSession) -> KamereonClient:
    """Fixture for testing Kamereon."""
    return get_logged_in_kamereon(websession=websession)


@pytest.mark.asyncio
async def test_get_person(kamereon: KamereonClient) -> None:
    """Test persons/{person_id} response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/person.json"),
        )
        response = await kamereon.get_person()
    assert response.accounts[0].accountId == "account-id-1"
    assert response.accounts[0].accountType == "MYRENAULT"
    assert response.accounts[0].accountStatus == "ACTIVE"

    assert response.accounts[1].accountId == "account-id-2"
    assert response.accounts[1].accountType == "SFDC"
    assert response.accounts[1].accountStatus == "ACTIVE"


@pytest.mark.parametrize("filename", get_json_files(f"{FIXTURE_PATH}/vehicles"))
@pytest.mark.asyncio
async def test_vehicles_response(filename: str, kamereon: KamereonClient) -> None:
    """Test accounts/{account_id}/vehicles response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_ACCOUNT_URL}/vehicles?{QUERY_STRING}",
            status=200,
            body=get_file_content(filename),
        )
        assert await kamereon.get_vehicles(TEST_ACCOUNT_ID)


@pytest.mark.asyncio
async def test_vehicle_battery_status(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/battery-status response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL2}/battery-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/battery-status.1.json"),
        )
        assert await kamereon.get_vehicle_battery_status(TEST_ACCOUNT_ID, TEST_VIN)


@pytest.mark.asyncio
async def test_vehicle_location(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/location response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/location?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/location.json"),
        )
        assert await kamereon.get_vehicle_location(TEST_ACCOUNT_ID, TEST_VIN)


@pytest.mark.asyncio
async def test_vehicle_hvac_status(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/hvac-status response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/hvac-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/hvac-status.json"),
        )
        assert await kamereon.get_vehicle_hvac_status(TEST_ACCOUNT_ID, TEST_VIN)


@pytest.mark.asyncio
async def test_vehicle_charge_mode(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/charge-mode response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/charge-mode?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/charge-mode.json"),
        )
        assert await kamereon.get_vehicle_charge_mode(TEST_ACCOUNT_ID, TEST_VIN)


@pytest.mark.asyncio
async def test_vehicle_cockpit(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/cockpit response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL2}/cockpit?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/cockpit.zoe.json"),
        )
        assert await kamereon.get_vehicle_cockpit(TEST_ACCOUNT_ID, TEST_VIN)


@pytest.mark.asyncio
async def test_vehicle_lock_status(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/lock-status response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/lock-status?{QUERY_STRING}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/lock-status.json"),
        )
        assert await kamereon.get_vehicle_lock_status(TEST_ACCOUNT_ID, TEST_VIN)


@pytest.mark.asyncio
async def test_vehicle_charging_settings(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/charging-settings response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/charging-settings?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_data/charging-settings.json"
            ),
        )
        assert await kamereon.get_vehicle_charging_settings(TEST_ACCOUNT_ID, TEST_VIN)


@pytest.mark.asyncio
async def test_vehicle_notification_settings(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/notification-settings response."""
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/notification-settings?{QUERY_STRING}",
            status=200,
            body=get_file_content(
                f"{FIXTURE_PATH}/vehicle_data/notification-settings.json"
            ),
        )
        assert await kamereon.get_vehicle_notification_settings(
            TEST_ACCOUNT_ID, TEST_VIN
        )


@pytest.mark.asyncio
async def test_vehicle_charges(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/vehicle-charges response."""
    params = {"start": "20201001", "end": "20201115"}
    query_string = f"{QUERY_STRING}&end=20201115&start=20201001"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/charges?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/charges.json"),
        )
        assert await kamereon.get_vehicle_charges(TEST_ACCOUNT_ID, TEST_VIN, params)


@pytest.mark.asyncio
async def test_vehicle_charge_history(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/charge-history response."""
    params = {"type": "month", "start": "202010", "end": "202011"}
    query_string = f"{QUERY_STRING}&end=202011&start=202010&type=month"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/charge-history?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/charge-history.json"),
        )
        assert await kamereon.get_vehicle_charge_history(
            TEST_ACCOUNT_ID, TEST_VIN, params
        )


@pytest.mark.asyncio
async def test_vehicle_hvac_sessions(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/hvac-sessions response."""
    params = {"start": "20201001", "end": "20201115"}
    query_string = f"{QUERY_STRING}&end=20201115&start=20201001"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/hvac-sessions?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/hvac-sessions.json"),
        )
        assert await kamereon.get_vehicle_hvac_sessions(
            TEST_ACCOUNT_ID, TEST_VIN, params
        )


@pytest.mark.asyncio
async def test_vehicle_hvac_history(kamereon: KamereonClient) -> None:
    """Test cars/{vin}/hvac-history response."""
    params = {"type": "month", "start": "202010", "end": "202011"}
    query_string = f"{QUERY_STRING}&end=202011&start=202010&type=month"
    with aioresponses() as mocked_responses:
        mocked_responses.get(
            f"{TEST_VEHICLE_URL1}/hvac-history?{query_string}",
            status=200,
            body=get_file_content(f"{FIXTURE_PATH}/vehicle_data/hvac-history.json"),
        )
        assert await kamereon.get_vehicle_hvac_history(
            TEST_ACCOUNT_ID, TEST_VIN, params
        )
