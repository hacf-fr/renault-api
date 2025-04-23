"""Test cases for the __main__ module."""

import json
import os
from typing import Any

import pytest
from aioresponses import aioresponses
from aioresponses.core import RequestCall
from click.testing import CliRunner
from syrupy.assertion import SnapshotAssertion
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


def test_vehicle_details(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
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

    assert result.output == snapshot


@pytest.mark.parametrize(
    "filename", fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicles")
)
def test_vehicle_status(
    mocked_responses: aioresponses,
    cli_runner: CliRunner,
    filename: str,
    snapshot: SnapshotAssertion,
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
    assert result.output == snapshot


def test_vehicle_status_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
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
    assert result.output == snapshot


def test_vehicle_status_no_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
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
    assert result.output == snapshot


def test_vehicle_status_json(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
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
    assert result.output == snapshot


def test_vehicle_contracts(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
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
    assert result.output == snapshot


def test_http_get(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
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
    assert result.output == snapshot


def test_http_get_list(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
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
    assert result.output == snapshot


def test_http_post(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
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
    json_body = json.dumps(body)
    result = cli_runner.invoke(
        __main__.main,
        f"http post {endpoint} '{json_body}'",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot


def test_http_post_file(
    tmpdir: Any,
    mocked_responses: aioresponses,
    cli_runner: CliRunner,
    snapshot: SnapshotAssertion,
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
    assert result.output == snapshot

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
