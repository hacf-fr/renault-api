"""Test suite for the renault_api package."""
from aioresponses import aioresponses
from tests import get_jwt
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN

GIGYA_FIXTURE_PATH = "tests/fixtures/gigya/"
KAMEREON_FIXTURE_PATH = "tests/fixtures/kamereon/"

DEFAULT_QUERY_STRING = f"country={TEST_COUNTRY}"
KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
ACCOUNT_PATH = f"accounts/{TEST_ACCOUNT_ID}"
ADAPTER_PATH = f"{ACCOUNT_PATH}"
ADAPTER_PATH = f"{ACCOUNT_PATH}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
ADAPTER2_PATH = f"{ACCOUNT_PATH}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"


def get_file_content(filename: str) -> str:
    """Read fixture text file as string."""
    with open(filename, "r") as file:
        content = file.read()
    return content


def inject_gigya(
    mocked_responses: aioresponses,
    urlpath: str,
    filename: str,
) -> None:
    """Inject Gigya data."""
    url = f"{TEST_GIGYA_URL}/{urlpath}"
    body = get_file_content(f"{GIGYA_FIXTURE_PATH}/{filename}")
    if filename.endswith("get_jwt.json"):
        body = body.replace("sample-jwt-token", get_jwt())
    mocked_responses.post(
        url,
        status=200,
        body=body,
        headers={"content-type": "text/javascript"},
    )


def inject_gigya_login(mocked_responses: aioresponses) -> None:
    """Inject Gigya login data."""
    inject_gigya(
        mocked_responses,
        "accounts.login",
        "login.json",
    )


def inject_gigya_account_info(mocked_responses: aioresponses) -> None:
    """Inject Gigya getAccountInfo data."""
    inject_gigya(
        mocked_responses,
        "accounts.getAccountInfo",
        "get_account_info.json",
    )


def inject_gigya_jwt(mocked_responses: aioresponses) -> None:
    """Inject Gigya getJWT data."""
    inject_gigya(
        mocked_responses,
        "accounts.getJWT",
        "get_jwt.json",
    )


def inject_gigya_all(mocked_responses: aioresponses) -> None:
    """Inject Gigya login/getAccountInfo/getJWT data."""
    inject_gigya_login(mocked_responses)
    inject_gigya_account_info(mocked_responses)
    inject_gigya_jwt(mocked_responses)


def inject_kamereon(
    mocked_responses: aioresponses,
    urlpath: str,
    filename: str,
) -> None:
    """Inject Kamereon data."""
    url = f"{KAMEREON_BASE_URL}/{urlpath}"
    body = get_file_content(f"{KAMEREON_FIXTURE_PATH}/{filename}")
    mocked_responses.get(
        url,
        status=200,
        body=body,
    )


def inject_kamereon_person(mocked_responses: aioresponses) -> None:
    """Inject sample person."""
    urlpath = f"persons/{TEST_PERSON_ID}?{DEFAULT_QUERY_STRING}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "person.json",
    )


def inject_kamereon_vehicles(mocked_responses: aioresponses) -> None:
    """Inject sample vehicles."""
    urlpath = f"accounts/{TEST_ACCOUNT_ID}/vehicles?{DEFAULT_QUERY_STRING}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "vehicles/zoe_40.1.json",
    )


def inject_kamereon_battery_status(mocked_responses: aioresponses) -> None:
    """Inject sample battery-status."""
    urlpath = f"{ADAPTER2_PATH}/battery-status?{DEFAULT_QUERY_STRING}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "vehicle_data/battery-status.1.json",
    )


def inject_kamereon_location(mocked_responses: aioresponses) -> None:
    """Inject sample location."""
    urlpath = f"{ADAPTER_PATH}/location?{DEFAULT_QUERY_STRING}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "vehicle_data/location.json",
    )


def inject_kamereon_hvac_status(mocked_responses: aioresponses) -> None:
    """Inject sample hvac-status."""
    urlpath = f"{ADAPTER_PATH}/hvac-status?{DEFAULT_QUERY_STRING}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "vehicle_data/hvac-status.json",
    )


def inject_kamereon_charge_mode(mocked_responses: aioresponses) -> None:
    """Inject sample charge-mode."""
    urlpath = f"{ADAPTER_PATH}/charge-mode?{DEFAULT_QUERY_STRING}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "vehicle_data/charge-mode.json",
    )


def inject_kamereon_charge_history(
    mocked_responses: aioresponses, start: str, end: str, period: str
) -> None:
    """Inject sample charges."""
    query_string = f"{DEFAULT_QUERY_STRING}&end={end}&start={start}&type={period}"
    urlpath = f"{ADAPTER_PATH}/charge-history?{query_string}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        f"vehicle_data/charge-history.{period}.json",
    )


def inject_kamereon_charges(
    mocked_responses: aioresponses, start: str, end: str
) -> None:
    """Inject sample charges."""
    query_string = f"{DEFAULT_QUERY_STRING}&end={end}&start={start}"
    urlpath = f"{ADAPTER_PATH}/charges?{query_string}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "vehicle_data/charges.json",
    )


def inject_kamereon_cockpit(mocked_responses: aioresponses) -> None:
    """Inject sample cockpit."""
    urlpath = f"{ADAPTER2_PATH}/cockpit?{DEFAULT_QUERY_STRING}"
    inject_kamereon(
        mocked_responses,
        urlpath,
        "vehicle_data/cockpit.zoe.json",
    )


def inject_vehicle_status(mocked_responses: aioresponses) -> None:
    """Inject Kamereon vehicle status data."""
    inject_kamereon_battery_status(mocked_responses)
    inject_kamereon_location(mocked_responses)
    inject_kamereon_hvac_status(mocked_responses)
    inject_kamereon_charge_mode(mocked_responses)
    inject_kamereon_cockpit(mocked_responses)
