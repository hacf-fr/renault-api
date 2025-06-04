"""Test suite for the renault_api package."""

from __future__ import annotations

import datetime
import json
from collections.abc import Mapping
from glob import glob
from os import path
from typing import Any

import jwt
from aioresponses import aioresponses
from marshmallow.schema import Schema

from tests.const import REDACTED
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN
from tests.const import TO_REDACT

GIGYA_FIXTURE_PATH = "tests/fixtures/gigya"
KAMEREON_FIXTURE_PATH = "tests/fixtures/kamereon"

DEFAULT_QUERY_STRING = f"country={TEST_COUNTRY}"
KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
ACCOUNT_PATH = f"accounts/{TEST_ACCOUNT_ID}"
ADAPTER_PATH = f"{ACCOUNT_PATH}/kamereon/kca/car-adapter/v1/cars/{TEST_VIN}"
KCM_ADAPTER_PATH = f"{ACCOUNT_PATH}/kamereon/kcm/v1/vehicles/{TEST_VIN}"
ADAPTER2_PATH = f"{ACCOUNT_PATH}/kamereon/kca/car-adapter/v2/cars/{TEST_VIN}"


def get_jwt(timedelta: datetime.timedelta | None = None) -> str:
    """Read fixture text file as string."""
    if not timedelta:
        timedelta = datetime.timedelta(seconds=900)
    encoded_jwt = jwt.encode(
        payload={"exp": datetime.datetime.utcnow() + timedelta},
        key="mock",
        algorithm="HS256",
    )
    return _jwt_as_string(encoded_jwt)


def _jwt_as_string(encoded_jwt: Any) -> str:
    """Ensure that JWT is returned as str."""
    if isinstance(encoded_jwt, str):  # pyjwt >= 2.0.0
        return encoded_jwt
    if isinstance(encoded_jwt, bytes):  # pyjwt < 2.0.0
        return encoded_jwt.decode("utf-8")
    raise ValueError("Unable to read JWT token.")


def get_json_files(parent_dir: str) -> list[str]:
    """Read fixture text file as string."""
    return [file.replace("\\", "/") for file in glob(f"{parent_dir}/*.json")]


def get_file_content(filename: str) -> str:
    """Read fixture text file as string."""
    with open(filename, encoding="utf-8") as file:
        content = file.read()
    return content


def get_file_content_as_schema(filename: str, schema: Schema) -> Any:
    """Read fixture text file as specified schema."""
    with open(filename, encoding="utf-8") as file:
        content = file.read()
    return schema.loads(content)


def get_file_content_as_wrapped_schema(
    filename: str, schema: Schema, wrap_in: str
) -> Any:
    """Read fixture text file as specified schema."""
    with open(filename) as file:
        content = file.read()
    content = f'{{"{wrap_in}": {content}}}'
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


def inject_gigya_login_invalid(mocked_responses: aioresponses) -> str:
    """Inject Gigya login data."""
    return inject_gigya(
        mocked_responses,
        "accounts.login",
        "login_invalid.txt",
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
    filename: str | None = None,
    *,
    body: str | None = None,
) -> str:
    """Inject Kamereon data."""
    url = f"{KAMEREON_BASE_URL}/{urlpath}"
    body = body or get_file_content(f"{KAMEREON_FIXTURE_PATH}/{filename}")
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


def inject_get_notifications(mocked_responses: aioresponses) -> str:
    """Inject sample charges."""
    urlpath = (
        f"persons/{TEST_PERSON_ID}/notifications/kmr?"
        "notificationId=ffcb0310-503f-4bc3-9056-e9d051a089c6&"
        f"{DEFAULT_QUERY_STRING}"
    )
    return inject_data(
        mocked_responses,
        urlpath,
        "person/notifications.1.json",
    )


def inject_get_vehicles(mocked_responses: aioresponses, vehicle: str) -> str:
    """Inject sample vehicles."""
    urlpath = f"accounts/{TEST_ACCOUNT_ID}/vehicles?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicles/{vehicle}",
    )


def inject_get_vehicle_details(mocked_responses: aioresponses, vehicle: str) -> str:
    """Inject sample vehicles."""
    urlpath = (
        f"accounts/{TEST_ACCOUNT_ID}/vehicles/{TEST_VIN}/details?{DEFAULT_QUERY_STRING}"
    )
    filename = f"vehicle_details/{vehicle}"
    if path.exists(f"{KAMEREON_FIXTURE_PATH}/{filename}"):
        return inject_data(
            mocked_responses,
            urlpath,
            filename,
        )
    # If we do not have a specific fixture, extract it from the vehicle list result
    filename = f"vehicles/{vehicle}"
    body = json.loads(get_file_content(f"{KAMEREON_FIXTURE_PATH}/{filename}"))
    return inject_data(
        mocked_responses,
        urlpath,
        body=json.dumps(body["vehicleLinks"][0]["vehicleDetails"]),
    )


def inject_get_car_adapter(mocked_responses: aioresponses, vehicle: str) -> str:
    """Inject sample vehicles."""
    urlpath = f"{ADAPTER2_PATH}?{DEFAULT_QUERY_STRING}"

    filename = f"vehicle_gateway/{vehicle}"
    return inject_data(
        mocked_responses,
        urlpath,
        filename,
    )


def inject_get_vehicle_contracts(mocked_responses: aioresponses, filename: str) -> str:
    """Inject sample contracts."""
    query_string = (
        "brand=RENAULT&"
        "connectedServicesContracts=true&"
        "country=FR&"
        "locale=fr_FR&"
        "warranty=true&"
        "warrantyMaintenanceContracts=true"
    )
    urlpath = f"accounts/{TEST_ACCOUNT_ID}/vehicles/{TEST_VIN}/contracts?{query_string}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicle_contract/{filename}",
    )


def inject_get_battery_status(
    mocked_responses: aioresponses, filename: str = "vehicle_data/battery-status.1.json"
) -> str:
    """Inject sample battery-status."""
    urlpath = f"{ADAPTER2_PATH}/battery-status?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        filename,
    )


def inject_get_tyre_pressure(
    mocked_responses: aioresponses, filename: str = "vehicle_data/pressure.json"
) -> str:
    """Inject sample tyre pressure."""
    urlpath = f"{ADAPTER_PATH}/pressure?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        filename,
    )


def inject_get_location(mocked_responses: aioresponses) -> str:
    """Inject sample location."""
    urlpath = f"{ADAPTER_PATH}/location?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/location.1.json",
    )


def inject_get_hvac_status(mocked_responses: aioresponses, vehicle: str) -> str:
    """Inject sample hvac-status."""
    urlpath = f"{ADAPTER_PATH}/hvac-status?{DEFAULT_QUERY_STRING}"
    filename = f"vehicle_data/hvac-status.{vehicle}.json"
    if not path.exists(f"{KAMEREON_FIXTURE_PATH}/{filename}"):
        filename = "vehicle_data/hvac-status.zoe.json"
        if vehicle in ["twingo_ze"]:
            filename = "vehicle_data/hvac-status.zoe_50.json"
    return inject_data(
        mocked_responses,
        urlpath,
        filename,
    )


def inject_get_hvac_settings(mocked_responses: aioresponses) -> str:
    """Inject sample hvac-settings."""
    urlpath = f"{ADAPTER_PATH}/hvac-settings?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/hvac-settings.json",
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


def inject_get_charges(
    mocked_responses: aioresponses,
    start: str,
    end: str,
    filename: str = "vehicle_data/charges.json",
) -> str:
    """Inject sample charges."""
    query_string = f"{DEFAULT_QUERY_STRING}&end={end}&start={start}"
    urlpath = f"{ADAPTER_PATH}/charges?{query_string}"
    return inject_data(
        mocked_responses,
        urlpath,
        filename,
    )


def inject_get_charging_settings(mocked_responses: aioresponses, type: str) -> str:
    """Inject sample charges."""
    urlpath = f"{ADAPTER_PATH}/charging-settings?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicle_data/charging-settings.{type}.json",
    )


def inject_get_charge_schedule(mocked_responses: aioresponses, type: str) -> str:
    """Inject sample charges."""
    urlpath = f"{ADAPTER_PATH}/charge-schedule?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicle_data/charge-schedule.{type}.json",
    )


def inject_get_ev_settings(mocked_responses: aioresponses, type: str) -> str:
    """Inject sample charges."""
    urlpath = f"{KCM_ADAPTER_PATH}/ev/settings?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        f"vehicle_kcm_data/ev-settings.{type}.json",
    )


def inject_get_cockpit(mocked_responses: aioresponses, vehicle: str) -> str:
    """Inject sample cockpit."""
    urlpath = f"{ADAPTER_PATH}/cockpit?{DEFAULT_QUERY_STRING}"
    filename = f"vehicle_data/cockpit.{vehicle}.json"
    if not path.exists(f"{KAMEREON_FIXTURE_PATH}/{filename}"):
        filename = "vehicle_data/cockpit.zoe.json"
    return inject_data(
        mocked_responses,
        urlpath,
        filename,
    )


def inject_get_lock_status(mocked_responses: aioresponses) -> str:
    """Inject sample lock-status."""
    urlpath = f"{ADAPTER_PATH}/lock-status?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/lock-status.1.json",
    )


def inject_get_res_state(mocked_responses: aioresponses) -> str:
    """Inject sample res-state."""
    urlpath = f"{ADAPTER_PATH}/res-state?{DEFAULT_QUERY_STRING}"
    return inject_data(
        mocked_responses,
        urlpath,
        "vehicle_data/res-state.1.json",
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


def inject_set_kcm_charge_pause_resume(
    mocked_responses: aioresponses, result: str
) -> str:
    """Inject sample charge-pause-resume."""
    urlpath = f"{KCM_ADAPTER_PATH}/charge/pause-resume?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        f"vehicle_kcm_action/charge-pause-resume.{result}.json",
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


def inject_set_hvac_schedules(mocked_responses: aioresponses) -> str:
    """Inject sample hvac-schedules."""
    urlpath = f"{ADAPTER2_PATH}/actions/hvac-schedule?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        "vehicle_action/hvac-schedule.schedules.json",
    )


def inject_start_horn(mocked_responses: aioresponses) -> str:
    """Inject sample horn-lights horn."""
    urlpath = f"{ADAPTER_PATH}/actions/horn-lights?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        "vehicle_action/horn-lights.horn.json",
    )


def inject_start_lights(mocked_responses: aioresponses) -> str:
    """Inject sample horn-lights lights."""
    urlpath = f"{ADAPTER_PATH}/actions/horn-lights?{DEFAULT_QUERY_STRING}"
    return inject_action(
        mocked_responses,
        urlpath,
        "vehicle_action/horn-lights.lights.json",
    )


def inject_vehicle_status(mocked_responses: aioresponses, vehicle: str) -> None:
    """Inject Kamereon vehicle status data."""
    inject_get_battery_status(mocked_responses)
    inject_get_location(mocked_responses)
    inject_get_lock_status(mocked_responses)
    inject_get_res_state(mocked_responses)
    inject_get_hvac_status(mocked_responses, vehicle)
    inject_get_charge_mode(mocked_responses)
    inject_get_cockpit(mocked_responses, vehicle)
    inject_get_tyre_pressure(mocked_responses)


def ensure_redacted(data: Mapping[str, Any], to_redact: list[str] = TO_REDACT) -> None:
    """Ensure all PII keys are redacted."""
    for key in to_redact:
        value = data.get(key)
        if value:
            assert isinstance(value, str)
            assert _is_redacted(key, value), f"Ensure {key} is redacted."


def _is_redacted(key: str, value: str) -> bool:
    """Ensure all PII keys are redacted."""
    if value == REDACTED:
        return True
    if key == "accountId":
        return value.startswith("account-id")
    if key == "vin":
        return value.startswith(("VF1AAAA", "UU1AAAA"))
    if key == "registrationNumber":
        return value == "REG-NUMBER"
    if key == "radioCode":
        return value == "1234"
    return False
