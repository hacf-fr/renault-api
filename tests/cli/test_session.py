"""Test cases for the __main__ module."""
import os
import pathlib
from typing import Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from aioresponses import aioresponses
from click.testing import CliRunner
from tests.const import TEST_LOCALE
from tests.const import TEST_LOCALE_DETAILS

from renault_api.cli import __main__
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL
from renault_api.const import CONF_LOCALE
from renault_api.credential_store import FileCredentialStore


@pytest.fixture
def runner(
    monkeypatch: MonkeyPatch, tmpdir: pathlib.Path
) -> Generator[CliRunner, None, None]:
    """Fixture for invoking command-line interfaces."""
    runner = CliRunner()

    monkeypatch.setattr("os.path.expanduser", lambda x: x.replace("~", str(tmpdir)))

    yield runner


def test_set_locale(mocked_responses: aioresponses, runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    for key in [
        CONF_LOCALE,
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        assert key not in credential_store

    result = runner.invoke(__main__.main, f"set --locale {TEST_LOCALE}")
    assert result.exit_code == 0

    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    for key in [
        CONF_LOCALE,
        CONF_GIGYA_APIKEY,
        CONF_GIGYA_URL,
        CONF_KAMEREON_APIKEY,
        CONF_KAMEREON_URL,
    ]:
        assert key in credential_store

    assert "" == result.output


def test_get_keys_succeeds(mocked_responses: aioresponses, runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main, f"set --locale {TEST_LOCALE}")
    assert result.exit_code == 0

    result = runner.invoke(__main__.main, "settings")
    assert result.exit_code == 0

    expected_output = (
        "Key                Value\n"
        f"{'-'*17}  {'-'*66}\n"
        f"locale             {TEST_LOCALE}\n"
        f"{CONF_GIGYA_URL}     {TEST_LOCALE_DETAILS[CONF_GIGYA_URL]}\n"
        f"{CONF_GIGYA_APIKEY}      {TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY]}\n"
        f"{CONF_KAMEREON_URL}  {TEST_LOCALE_DETAILS[CONF_KAMEREON_URL]}\n"
        f"{CONF_KAMEREON_APIKEY}   {TEST_LOCALE_DETAILS[CONF_KAMEREON_APIKEY]}\n"
    )
    assert expected_output == result.output
