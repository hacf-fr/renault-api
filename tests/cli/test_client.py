"""Test cases for the __main__ module."""
import os
import pathlib
from typing import Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from aioresponses import aioresponses
from click.testing import CliRunner
from tests import get_file_content
from tests import get_jwt
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_LOCALE_DETAILS
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.cli import __main__
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import FileCredentialStore
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya import GIGYA_PERSON_ID

# from renault_api.cli.renault_settings import CLICredentialStore


TEST_KAMEREON_BASE_URL = f"{TEST_KAMEREON_URL}/commerce/v1"
FIXTURE_PATH = "tests/fixtures/kamereon/"
QUERY_STRING = f"country={TEST_COUNTRY}"
TEST_GIGYA_URL = TEST_LOCALE_DETAILS[CONF_GIGYA_URL]
GIGYA_FIXTURE_PATH = "tests/fixtures/gigya/"


@pytest.fixture
def runner(
    monkeypatch: MonkeyPatch, tmpdir: pathlib.Path
) -> Generator[CliRunner, None, None]:
    """Fixture for invoking command-line interfaces."""
    runner = CliRunner()

    monkeypatch.setattr("os.path.expanduser", lambda x: x.replace("~", str(tmpdir)))

    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(get_jwt())

    for key in [
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        credential_store[key] = Credential(TEST_LOCALE_DETAILS[key])

    yield runner


@pytest.fixture
def clean_runner(
    monkeypatch: MonkeyPatch, tmpdir: pathlib.Path
) -> Generator[CliRunner, None, None]:
    """Fixture for invoking command-line interfaces."""
    runner = CliRunner()

    monkeypatch.setattr("os.path.expanduser", lambda x: x.replace("~", str(tmpdir)))

    yield runner


def test_login_prompt(mocked_responses: aioresponses, clean_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    mocked_responses.post(
        f"{TEST_GIGYA_URL}/accounts.login",
        status=200,
        body=get_file_content(f"{GIGYA_FIXTURE_PATH}/login.json"),
        headers={"content-type": "text/javascript"},
    )
    mocked_responses.post(
        f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
        status=200,
        body=get_file_content(f"{GIGYA_FIXTURE_PATH}/get_account_info.json"),
        headers={"content-type": "text/javascript"},
    )
    mocked_responses.post(
        f"{TEST_GIGYA_URL}/accounts.getJWT",
        status=200,
        body=get_file_content(f"{GIGYA_FIXTURE_PATH}/get_jwt.json"),
        headers={"content-type": "text/javascript"},
    )

    mocked_responses.get(
        f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
        status=200,
        body=get_file_content(f"{FIXTURE_PATH}/person.json"),
    )

    result = clean_runner.invoke(
        __main__.main,
        "--debug login",
        input=f"{TEST_USERNAME}\n{TEST_PASSWORD}\n{TEST_LOCALE}\ny",
    )
    assert result.exit_code == 0, result.exception
    expected_output = (
        f"User: {TEST_USERNAME}\n"
        "Password: \n"
        f"Please select a locale [fr_FR]: {TEST_LOCALE}\n"
        "Do you want to save the locale to the credential store? [y/N]: y\n"
    )
    assert expected_output == result.output


def test_login_no_prompt(
    mocked_responses: aioresponses, clean_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    mocked_responses.post(
        f"{TEST_GIGYA_URL}/accounts.login",
        status=200,
        body=get_file_content(f"{GIGYA_FIXTURE_PATH}/login.json"),
        headers={"content-type": "text/javascript"},
    )
    mocked_responses.post(
        f"{TEST_GIGYA_URL}/accounts.getAccountInfo",
        status=200,
        body=get_file_content(f"{GIGYA_FIXTURE_PATH}/get_account_info.json"),
        headers={"content-type": "text/javascript"},
    )
    mocked_responses.post(
        f"{TEST_GIGYA_URL}/accounts.getJWT",
        status=200,
        body=get_file_content(f"{GIGYA_FIXTURE_PATH}/get_jwt.json"),
        headers={"content-type": "text/javascript"},
    )

    mocked_responses.get(
        f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}",
        status=200,
        body=get_file_content(f"{FIXTURE_PATH}/person.json"),
    )

    result = clean_runner.invoke(
        __main__.main,
        f"--debug --locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
    )
    assert result.exit_code == 0, result.exception
    assert "" == result.output


def test_list_accounts(mocked_responses: aioresponses, runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    for key in [
        CONF_LOCALE,
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        assert key in credential_store

    url = f"{TEST_KAMEREON_BASE_URL}/persons/{TEST_PERSON_ID}?{QUERY_STRING}"
    mocked_responses.get(
        url,
        status=200,
        body=get_file_content(f"{FIXTURE_PATH}/person.json"),
    )

    result = runner.invoke(__main__.main, "accounts")  # , input="test\ntest")
    assert result.exit_code == 0, result.exception

    expected_output = (
        "Type       ID\n"
        "---------  ------------\n"
        "MYRENAULT  account-id-1\n"
        "SFDC       account-id-2\n"
    )
    assert expected_output == result.output
