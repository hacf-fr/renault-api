"""Test cases for the __main__ module."""

import json
import os
from locale import getdefaultlocale
from typing import Any

import pytest
from aioresponses import aioresponses
from aioresponses.core import RequestCall
from click.testing import CliRunner
from typeguard import suppress_type_checks
from yarl import URL

from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_LOCALE
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.const import TEST_VIN

from renault_api.cli import __main__
from renault_api.cli.renault_settings import CONF_ACCOUNT_ID
from renault_api.cli.renault_settings import CONF_VIN
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import FileCredentialStore
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya import GIGYA_PERSON_ID

EXPECTED_STATUS = {
    "captur_ii.1.json": (
        "--------------------  ----------------------\n"
        "Total mileage         5566.78 km\n"
        "Fuel autonomy         35.0 km\n"
        "Fuel quantity         3.0 L\n"
        "GPS Latitude          48.1234567\n"
        "GPS Longitude         11.1234567\n"
        "GPS last updated      2020-02-18 17:58:38\n"
        "Lock status           locked\n"
        "Lock last updated     2022-02-02 14:51:13\n"
        "Engine state          Stopped, ready for RES\n"
        "Front left pressure   2460 bar\n"
        "Front right pressure  2730 bar\n"
        "Rear left pressure    2790 bar\n"
        "Rear right pressure   2790 bar\n"
        "--------------------  ----------------------\n"
    ),
    "captur_ii.2.json": (
        "--------------------  -------------------------\n"
        "Battery level         50 %\n"
        "Last updated          2020-11-17 09:06:48\n"
        "Range estimate        128 km\n"
        "Plug state            PlugState.UNPLUGGED\n"
        "Charging state        ChargeState.NOT_IN_CHARGE\n"
        "Charge mode           always\n"
        "Total mileage         5566.78 km\n"
        "Fuel autonomy         35.0 km\n"
        "Fuel quantity         3.0 L\n"
        "GPS Latitude          48.1234567\n"
        "GPS Longitude         11.1234567\n"
        "GPS last updated      2020-02-18 17:58:38\n"
        "Lock status           locked\n"
        "Lock last updated     2022-02-02 14:51:13\n"
        "Engine state          Stopped, ready for RES\n"
        "Front left pressure   2460 bar\n"
        "Front right pressure  2730 bar\n"
        "Rear left pressure    2790 bar\n"
        "Rear right pressure   2790 bar\n"
        "--------------------  -------------------------\n"
    ),
    "twingo_ze.1.json": (
        "--------------------  -------------------------\n"
        "Battery level         50 %\n"
        "Last updated          2020-11-17 09:06:48\n"
        "Range estimate        128 km\n"
        "Plug state            PlugState.UNPLUGGED\n"
        "Charging state        ChargeState.NOT_IN_CHARGE\n"
        "Charge mode           always\n"
        "Total mileage         49114.27 km\n"
        "GPS Latitude          48.1234567\n"
        "GPS Longitude         11.1234567\n"
        "GPS last updated      2020-02-18 17:58:38\n"
        "Lock status           locked\n"
        "Lock last updated     2022-02-02 14:51:13\n"
        "Engine state          Stopped, ready for RES\n"
        "HVAC status           on\n"
        "Front left pressure   2460 bar\n"
        "Front right pressure  2730 bar\n"
        "Rear left pressure    2790 bar\n"
        "Rear right pressure   2790 bar\n"
        "--------------------  -------------------------\n"
    ),
    "zoe_40.1.json": (
        "--------------------  -------------------------\n"
        "Battery level         50 %\n"
        "Last updated          2020-11-17 09:06:48\n"
        "Range estimate        128 km\n"
        "Plug state            PlugState.UNPLUGGED\n"
        "Charging state        ChargeState.NOT_IN_CHARGE\n"
        "Charge mode           always\n"
        "Total mileage         49114.27 km\n"
        "Engine state          Stopped, ready for RES\n"
        "HVAC status           off\n"
        "External temperature  8.0 °C\n"
        "Front left pressure   2460 bar\n"
        "Front right pressure  2730 bar\n"
        "Rear left pressure    2790 bar\n"
        "Rear right pressure   2790 bar\n"
        "--------------------  -------------------------\n"
    ),
    "zoe_40.2.json": (
        "--------------------  -------------------------\n"
        "Battery level         50 %\n"
        "Last updated          2020-11-17 09:06:48\n"
        "Range estimate        128 km\n"
        "Plug state            PlugState.UNPLUGGED\n"
        "Charging state        ChargeState.NOT_IN_CHARGE\n"
        "Charge mode           always\n"
        "Total mileage         49114.27 km\n"
        "Engine state          Stopped, ready for RES\n"
        "HVAC status           off\n"
        "External temperature  8.0 °C\n"
        "Front left pressure   2460 bar\n"
        "Front right pressure  2730 bar\n"
        "Rear left pressure    2790 bar\n"
        "Rear right pressure   2790 bar\n"
        "--------------------  -------------------------\n"
    ),
    "zoe_50.1.json": (
        "--------------------  -------------------------\n"
        "Battery level         50 %\n"
        "Last updated          2020-11-17 09:06:48\n"
        "Range estimate        128 km\n"
        "Plug state            PlugState.UNPLUGGED\n"
        "Charging state        ChargeState.NOT_IN_CHARGE\n"
        "Charge mode           always\n"
        "Total mileage         5785.75 km\n"
        "Fuel autonomy         0.0 km\n"
        "Fuel quantity         0.0 L\n"
        "GPS Latitude          48.1234567\n"
        "GPS Longitude         11.1234567\n"
        "GPS last updated      2020-02-18 17:58:38\n"
        "Lock status           locked\n"
        "Lock last updated     2022-02-02 14:51:13\n"
        "Engine state          Stopped, ready for RES\n"
        "HVAC status           on\n"
        "Front left pressure   2460 bar\n"
        "Front right pressure  2730 bar\n"
        "Rear left pressure    2790 bar\n"
        "Rear right pressure   2790 bar\n"
        "--------------------  -------------------------\n"
    ),
    "zoe_40.1_json.json": (
        '{"battery-status": {"timestamp": "2020-11-17T09:06:48+01:00", '
        '"batteryLevel": 50, "batteryAutonomy": 128, "batteryCapacity": 0, '
        '"batteryAvailableEnergy": 0, "plugStatus": 0, "chargingStatus": -1.0}, '
        '"charge-mode": {"chargeMode": "always"}, '
        '"cockpit": {"totalMileage": 49114.27}, '
        '"res-state": {"details": "Stopped, ready for RES", "code": "10"}, '
        '"hvac-status": {"externalTemperature": 8.0, "hvacStatus": "off"}, '
        '"pressure": {"flPressure": 2460, "frPressure": 2730, '
        '"rlPressure": 2790, "rrPressure": 2790, '
        '"flStatus": 0, "frStatus": 0, '
        '"rlStatus": 0, "rrStatus": 0}}\n'
    ),
}


def test_vehicle_details(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")

    result = cli_runner.invoke(__main__.main, "vehicle")
    assert result.exit_code == 0, result.exception

    expected_output = (
        "Registration    Brand    Model    VIN\n"
        "--------------  -------  -------  -----------------\n"
        "REG-NUMBER      RENAULT  ZOE      VF1AAAAA555777999\n"
    )
    assert expected_output == result.output


@pytest.mark.parametrize(
    "filename", fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicles")
)
def test_vehicle_status(
    mocked_responses: aioresponses, cli_runner: CliRunner, filename: str
) -> None:
    """It exits with a status code of zero."""
    filename = os.path.basename(filename)
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_details(mocked_responses, filename)
    if filename in [
        "captur_ii.1.json",
        "captur_ii.2.json",
    ]:
        fixtures.inject_vehicle_status(mocked_responses, "captur_ii")
    elif filename in [
        "twingo_ze.1.json",
    ]:
        fixtures.inject_vehicle_status(mocked_responses, "twingo_ze")
    elif filename in [
        "zoe_50.1.json",
    ]:
        fixtures.inject_vehicle_status(mocked_responses, "zoe_50")
    else:
        fixtures.inject_vehicle_status(mocked_responses, "zoe")

    result = cli_runner.invoke(__main__.main, "status")
    assert result.exit_code == 0, result.exception

    if filename in EXPECTED_STATUS:
        assert EXPECTED_STATUS[filename] == result.output


def test_vehicle_status_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_all(mocked_responses)
    fixtures.inject_get_person(mocked_responses)

    # Injected for account selection
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")
    vehicle2_urlpath = f"accounts/account-id-2/vehicles?{fixtures.DEFAULT_QUERY_STRING}"
    fixtures.inject_data(
        mocked_responses,
        vehicle2_urlpath,
        "vehicles/zoe_40.1.json",
    )

    # Injected again for vehicle selection
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")

    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.2.json")
    fixtures.inject_vehicle_status(mocked_responses, "zoe")

    result = cli_runner.invoke(
        __main__.main,
        "status",
        input=f"{TEST_LOCALE}\nN\n{TEST_USERNAME}\n{TEST_PASSWORD}\n1\ny\n1\ny\n",
    )
    assert result.exit_code == 0, result.exception

    default_locale = getdefaultlocale()[0]
    prompt_default = f" [{default_locale}]" if default_locale else ""

    expected_output = (
        f"Please select a locale{prompt_default}: {TEST_LOCALE}\n"
        "Do you want to save the locale to the credential store? [y/N]: N\n"
        "\n"
        f"User: {TEST_USERNAME}\n"
        "Password: \n"
        "\n"
        "    ID            Type         Vehicles\n"
        "--  ------------  ---------  ----------\n"
        " 1  account-id-1  MYRENAULT           1\n"
        " 2  account-id-2  SFDC                1\n"
        "\n"
        "Please select account [1]: 1\n"
        "Do you want to save the account ID to the credential store? [y/N]: y\n"
        "\n"
        "    Vin                Registration    Brand    Model\n"
        "--  -----------------  --------------  -------  -------\n"
        " 1  VF1AAAAA555777999  REG-NUMBER      RENAULT  ZOE\n"
        "\n"
        "Please select vehicle [1]: 1\n"
        "Do you want to save the VIN to the credential store? [y/N]: y\n"
        "\n"
        f"{EXPECTED_STATUS['zoe_40.1.json']}"
    )
    assert expected_output == result.output


def test_vehicle_status_no_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.2.json")
    fixtures.inject_vehicle_status(mocked_responses, "zoe")

    result = cli_runner.invoke(
        __main__.main, f"--account {TEST_ACCOUNT_ID} --vin {TEST_VIN} status"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_STATUS["zoe_40.1.json"] == result.output


def test_vehicle_status_json(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.2.json")
    fixtures.inject_vehicle_status(mocked_responses, "zoe")

    result = cli_runner.invoke(
        __main__.main, f"--account {TEST_ACCOUNT_ID} --vin {TEST_VIN} --json status"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_STATUS["zoe_40.1_json.json"] == result.output


def test_vehicle_contracts(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.1.json")

    result = cli_runner.invoke(__main__.main, "contracts")
    assert result.exit_code == 0, result.exception

    expected_output = (
        "Type                            Code                  "
        "Description                       Start       End         Status\n"
        "------------------------------  --------------------  "
        "--------------------------------  ----------  ----------  "
        "------------------\n"
        "WARRANTY_MAINTENANCE_CONTRACTS  40                    "
        "CONTRAT LOSANGE                   2018-04-04  2022-04-03  Actif\n"
        "CONNECTED_SERVICES              ZECONNECTP            "
        "My Z.E. Connect en série 36 mois  2018-08-23  2021-08-23  Actif\n"
        "CONNECTED_SERVICES              GBA                   "
        "Battery Services                  2018-03-23              "
        "Echec d’activation\n"
        "WARRANTY                        ManufacturerWarranty  "
        "Garantie fabricant                            2020-04-03  Expiré\n"
        "WARRANTY                        PaintingWarranty      "
        "Garantie peinture                             2021-04-03  Actif\n"
        "WARRANTY                        CorrosionWarranty     "
        "Garantie corrosion                            2030-04-03  Actif\n"
        "WARRANTY                        GMPeWarranty          "
        "Garantie GMPe                                 2020-04-03  Expiré\n"
        "WARRANTY                        AssistanceWarranty    "
        "Garantie assistance                           2020-04-03  Expiré\n"
    )
    assert expected_output == result.output


def test_http_get(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_charging_settings(mocked_responses, "single")

    endpoint = (
        "/commerce/v1/accounts/{account_id}"
        "/kamereon/kca/car-adapter"
        "/v1/cars/{vin}/charging-settings"
    )
    result = cli_runner.invoke(
        __main__.main,
        f"http get {endpoint}",
    )
    assert result.exit_code == 0, result.exception

    expected_output = (
        "{'data': {'type': 'Car', 'id': 'VF1AAAAA555777999', 'attributes': {"
        "'mode': 'scheduled', 'schedules': ["
        "{'id': 1, 'activated': True, "
        "'monday': {'startTime': 'T12:00Z', 'duration': 15}, "
        "'tuesday': {'startTime': 'T04:30Z', 'duration': 420}, "
        "'wednesday': {'startTime': 'T22:30Z', 'duration': 420}, "
        "'thursday': {'startTime': 'T22:00Z', 'duration': 420}, "
        "'friday': {'startTime': 'T12:15Z', 'duration': 15}, "
        "'saturday': {'startTime': 'T12:30Z', 'duration': 30}, "
        "'sunday': {'startTime': 'T12:45Z', 'duration': 45}}"
        "]}}}\n"
    )
    assert expected_output == result.output


def test_http_get_list(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    print(fixtures.inject_get_notifications(mocked_responses))

    endpoint = (
        "/commerce/v1/persons/person-id-1"
        "/notifications/kmr?notificationId=ffcb0310-503f-4bc3-9056-e9d051a089c6"
    )
    result = cli_runner.invoke(
        __main__.main,
        f"http get {endpoint}",
    )
    assert result.exit_code == 0, result.exception

    expected_output = (
        "{'data': [{'notificationId': 'ffcb0310-503f-4bc3-9056-e9d051a089c6', "
        "'notifDate': '2022-02-01T19:01:51.622', 'vin': '*PRIVATE*', "
        "'personId': '*PRIVATE*', 'kmrUserId': '*PRIVATE*', "
        "'actionType': 'COMMAND_RESPONSE', 'commandResponse': {'status': 'CREATED'}, "
        "'commandType': 'SRP_SETS'}, "
        "{'notificationId': 'ffcb0310-503f-4bc3-9056-e9d051a089c6', "
        "'notifDate': '2022-02-01T19:01:51.623', 'vin': '*PRIVATE*', "
        "'personId': '*PRIVATE*', 'kmrUserId': '*PRIVATE*', "
        "'actionType': 'SRP_SALT_REQUEST', 'srpResponse': {'status': 'OK', 'loginB': "
        "'*PRIVATE*', 'loginSalt': '*PRIVATE*'}}]}\n"
    )
    assert expected_output == result.output


def test_http_post(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    endpoint = (
        "/commerce/v1/accounts/{account_id}"
        "/kamereon/kca/car-adapter"
        "/v2/cars/{vin}/actions/charge-schedule"
    )
    body = {"data": {"type": "ChargeSchedule", "attributes": {"schedules": []}}}
    json_body = json.dumps(body)
    result = cli_runner.invoke(
        __main__.main,
        f"http post {endpoint} '{json_body}'",
    )
    assert result.exit_code == 0, result.exception

    expected_output = (
        "{'data': {'type': 'ChargeSchedule', 'id': 'guid', "
        "'attributes': {'schedules': ["
        "{'id': 1, 'activated': True, "
        "'tuesday': {'startTime': 'T04:30Z', 'duration': 420}, "
        "'wednesday': {'startTime': 'T22:30Z', 'duration': 420}, "
        "'thursday': {'startTime': 'T22:00Z', 'duration': 420}, "
        "'friday': {'startTime': 'T23:30Z', 'duration': 480}, "
        "'saturday': {'startTime': 'T18:30Z', 'duration': 120}, "
        "'sunday': {'startTime': 'T12:45Z', 'duration': 45}}]}}}\n"
    )
    assert expected_output == result.output

    expected_json = {
        "data": {"type": "ChargeSchedule", "attributes": {"schedules": []}}
    }

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]


def test_http_post_file(
    tmpdir: Any, mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    endpoint = (
        "/commerce/v1/accounts/{account_id}"
        "/kamereon/kca/car-adapter"
        "/v2/cars/{vin}/actions/charge-schedule"
    )
    body = {"data": {"type": "ChargeSchedule", "attributes": {"schedules": []}}}

    json_file = tmpdir.mkdir("json").join("sample.json")
    json_file.write(json.dumps(body))

    with suppress_type_checks():
        result = cli_runner.invoke(
            __main__.main,
            f"http post-file {endpoint} '{json_file}'",
        )
    assert result.exit_code == 0, result.exception

    expected_output = (
        "{'data': {'type': 'ChargeSchedule', 'id': 'guid', "
        "'attributes': {'schedules': ["
        "{'id': 1, 'activated': True, "
        "'tuesday': {'startTime': 'T04:30Z', 'duration': 420}, "
        "'wednesday': {'startTime': 'T22:30Z', 'duration': 420}, "
        "'thursday': {'startTime': 'T22:00Z', 'duration': 420}, "
        "'friday': {'startTime': 'T23:30Z', 'duration': 480}, "
        "'saturday': {'startTime': 'T18:30Z', 'duration': 120}, "
        "'sunday': {'startTime': 'T12:45Z', 'duration': 45}}]}}}\n"
    )
    assert expected_output == result.output

    expected_json = {
        "data": {"type": "ChargeSchedule", "attributes": {"schedules": []}}
    }

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
