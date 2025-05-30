"""Test cases for the __main__ module."""

import os

from aioresponses import aioresponses
from click.testing import CliRunner
from syrupy.assertion import SnapshotAssertion

from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_LOCALE
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.cli import __main__
from renault_api.cli.renault_settings import CONF_ACCOUNT_ID
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import FileCredentialStore
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya import GIGYA_PERSON_ID


def test_list_vehicles_prompt(
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

    # Injected again for vehicle listing
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")

    result = cli_runner.invoke(
        __main__.main,
        "vehicles",
        input=f"{TEST_LOCALE}\nN\n{TEST_USERNAME}\n{TEST_PASSWORD}\n1\ny\n",
    )
    assert result.exit_code == 0, result.exception

    assert result.output == snapshot


def test_list_vehicles_store(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")

    result = cli_runner.invoke(__main__.main, "vehicles")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_list_vehicles_no_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")

    result = cli_runner.invoke(__main__.main, f"--account {TEST_ACCOUNT_ID} vehicles")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot
