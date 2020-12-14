"""Test suite for the renault_api package."""
import datetime
from glob import glob
from typing import Any
from typing import List
from typing import Optional

import jwt
from aioresponses import aioresponses
from marshmallow.schema import Schema
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN

GIGYA_FIXTURE_PATH = "tests/fixtures/gigya"
KAMEREON_FIXTURE_PATH = "tests/fixtures/kamereon"

DEFAULT_QUERY_STRING = f"country={TEST_COUNTRY}"
KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
ACCOUNT_PATH = f"accounts/{TEST_ACCOUNT_ID}"
ADAPTER_PATH = f"{ACCOUNT_PATH}"
ADAPTER_PATH = f"{ACCOUNT_PATH}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
ADAPTER2_PATH = f"{ACCOUNT_PATH}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"


def get_jwt(timedelta: Optional[datetime.timedelta] = None) -> str:
    """Read fixture text file as string."""
    if not timedelta:
        timedelta = datetime.timedelta(seconds=900)
    return jwt.encode(
        payload={"exp": datetime.datetime.utcnow() + timedelta},
        key="mock",
        algorithm="HS256",
    ).decode("utf-8")


def get_json_files(parent_dir: str) -> List[str]:
    """Read fixture text file as string."""
    return glob(f"{parent_dir}/*.json")


def get_file_content(filename: str) -> str:
    """Read fixture text file as string."""
    with open(filename, "r") as file:
        content = file.read()
    return content


def get_file_content_as_schema(filename: str, schema: Schema) -> Any:
    """Read fixture text file as specified schema."""
    with open(filename, "r") as file:
        content = file.read()
    return schema.loads(content)


def inject_gigya(
    mocked_responses: aioresponses,
    urlpath: str,
    filename: str,
) -> str:
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
    return url


def inject_gigya_login(mocked_responses: aioresponses) -> str:
    """Inject Gigya login data."""
    return inject_gigya(
        mocked_responses,
        "accounts.login",
        "login.json",
    )


def inject_gigya_account_info(mocked_responses: aioresponses) -> str:
    """Inject Gigya getAccountInfo data."""
    return inject_gigya(
        mocked_responses,
        "accounts.getAccountInfo",
        "get_account_info.json",
    )


def inject_gigya_jwt(mocked_responses: aioresponses) -> str:
    """Inject Gigya getJWT data."""
    return inject_gigya(
        mocked_responses,
        "accounts.getJWT",
        "get_jwt.json",
    )


def inject_gigya_all(mocked_responses: aioresponses) -> None:
    """Inject Gigya login/getAccountInfo/getJWT data."""
    inject_gigya_login(mocked_responses)
    inject_gigya_account_info(mocked_responses)
    inject_gigya_jwt(mocked_responses)


def inject_data(
    mocked_responses: aioresponses,
    urlpath: str,
    filename: str,
) -> str:
    """Inject Kamereon data."""
    url = f"{KAMEREON_BASE_URL}/{urlpath}"
    body = get_file_content(f"{KAMEREON_FIXTURE_PATH}/{filename}")
    mocked_responses.get(
        url,
        status=200,
        body=body,
    )
    return url


def inject_action(
    mocked_responses: aioresponses,
    urlpath: str,
    filename: str,
) -> str:
    """Inject Kamereon data."""
    url = f"{KAMEREON_BASE_URL}/{urlpath}"
    body = get_file_content(f"{KAMEREON_FIXTURE_PATH}/{filename}")
    mocked_responses.post(
        url,
        status=200,
        body=body,
    )
    return url


def inject_get_person(mocked_responses: aioresponses) -> str:
    """Inject sample person."""
    urlpath = f"persons/{TEST_PERSON_ID}?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "person.json",
    )


def inject_get_vehicles(mocked_responses: aioresponses, vehicle: str) -> str:
    """Inject sample vehicles."""
    urlpath = f"accounts/{TEST_ACCOUNT_ID}/vehicles?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicles/{vehicle}.json",
    )


def inject_get_battery_status(mocked_responses: aioresponses) -> str:
    """Inject sample battery-status."""
    urlpath = f"{ADAPTER2_PATH}/battery-status?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/battery-status.1.json",
    )


def inject_get_location(mocked_responses: aioresponses) -> str:
    """Inject sample location."""
    urlpath = f"{ADAPTER_PATH}/location?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/location.json",
    )


def inject_get_hvac_status(mocked_responses: aioresponses) -> str:
    """Inject sample hvac-status."""
    urlpath = f"{ADAPTER_PATH}/hvac-status?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/hvac-status.json",
    )


def inject_get_charge_mode(mocked_responses: aioresponses) -> str:
    """Inject sample charge-mode."""
    urlpath = f"{ADAPTER_PATH}/charge-mode?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/charge-mode.json",
    )


def inject_get_charge_history(
    mocked_responses: aioresponses, start: str, end: str, period: str
) -> str:
    """Inject sample charge-history."""
    query_string = f"{DEFAULT_QUERY_STRING}&end={end}&start={start}&type={period}"
    urlpath = f"{ADAPTER_PATH}/charge-history?{query_string}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicle_data/charge-history.{period}.json",
    )


def inject_get_hvac_history(
    mocked_responses: aioresponses, start: str, end: str, period: str
) -> str:
    """Inject sample hvac-history."""
    query_string = f"{DEFAULT_QUERY_STRING}&end={end}&start={start}&type={period}"
    urlpath = f"{ADAPTER_PATH}/hvac-history?{query_string}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/hvac-history.json",
    )


def inject_get_hvac_sessions(
    mocked_responses: aioresponses, start: str, end: str
) -> str:
    """Inject sample hvac-sessions."""
    query_string = f"{DEFAULT_QUERY_STRING}&end={end}&start={start}"
    urlpath = f"{ADAPTER_PATH}/hvac-sessions?{query_string}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/hvac-sessions.json",
    )


def inject_get_charges(mocked_responses: aioresponses, start: str, end: str) -> str:
    """Inject sample charges."""
    query_string = f"{DEFAULT_QUERY_STRING}&end={end}&start={start}"
    urlpath = f"{ADAPTER_PATH}/charges?{query_string}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/charges.json",
    )


def inject_get_charging_settings(mocked_responses: aioresponses) -> str:
    """Inject sample charges."""
    urlpath = f"{ADAPTER_PATH}/charging-settings?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/charging-settings.json",
    )


def inject_get_cockpit(mocked_responses: aioresponses, vehicle: str) -> str:
    """Inject sample cockpit."""
    urlpath = f"{ADAPTER2_PATH}/cockpit?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicle_data/cockpit.{vehicle}.json",
    )


def inject_get_lock_status(mocked_responses: aioresponses) -> str:
    """Inject sample lock-status."""
    urlpath = f"{ADAPTER_PATH}/lock-status?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/lock-status.json",
    )


def inject_get_notification_settings(mocked_responses: aioresponses) -> str:
    """Inject sample notification-settings."""
    urlpath = f"{ADAPTER_PATH}/notification-settings?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/notification-settings.json",
    )


def inject_set_charge_mode(mocked_responses: aioresponses, mode: str) -> str:
    """Inject sample charge-mode."""
    urlpath = f"{ADAPTER_PATH}/actions/charge-mode?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        f"vehicle_action/charge-mode.{mode}.json",
    )


def inject_set_charge_schedule(mocked_responses: aioresponses, result: str) -> str:
    """Inject sample charge-schedule."""
    urlpath = f"{ADAPTER2_PATH}/actions/charge-schedule?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        f"vehicle_action/charge-schedule.{result}.json",
    )


def inject_set_charging_start(mocked_responses: aioresponses, result: str) -> str:
    """Inject sample charge-mode."""
    urlpath = f"{ADAPTER_PATH}/actions/charging-start?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        f"vehicle_action/charging-start.{result}.json",
    )


def inject_set_hvac_start(mocked_responses: aioresponses, result: str) -> str:
    """Inject sample hvac-start."""
    urlpath = f"{ADAPTER_PATH}/actions/hvac-start?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        f"vehicle_action/hvac-start.{result}.json",
    )


def inject_vehicle_status(mocked_responses: aioresponses) -> None:
    """Inject Kamereon vehicle status data."""
    inject_get_battery_status(mocked_responses)
    inject_get_location(mocked_responses)
    inject_get_hvac_status(mocked_responses)
    inject_get_charge_mode(mocked_responses)
    inject_get_cockpit(mocked_responses, "zoe")
