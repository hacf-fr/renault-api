"""Test cases for the __main__ module."""

import os
import pathlib
from collections.abc import Generator
from datetime import datetime
from importlib import metadata as imp_metadata
from typing import Any

from _pytest.fixtures import fixture
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from tests.const import TEST_LOCALE

from renault_api.cli import __main__

PATCH_TODAY = datetime(2018, 12, 25)


@fixture
def patch_root(tmpdir: pathlib.Path) -> Generator[None, None, None]:
    """Update current directory to test log folder."""
    root_dir = os.getcwd()
    os.chdir(tmpdir)
    yield
    os.chdir(root_dir)


@fixture
def patch_datetime(monkeypatch: MonkeyPatch) -> Generator[None, None, None]:
    """Allow override of __main__.datetime methods."""

    class MyDatetime:
        @classmethod
        def today(cls) -> datetime:
            """Force today to return a static date."""
            return PATCH_TODAY

    monkeypatch.setattr("renault_api.cli.__main__.datetime", MyDatetime)
    yield


def test_main_succeeds(cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    click_version_str = imp_metadata.version("click")
    click_version_parts = tuple(int(part) for part in click_version_str.split(".")[:2])
    result = cli_runner.invoke(__main__.main)
    assert result.exit_code == (
        2 if click_version_parts >= (8, 2) else 0
    ), result.exception


def test_debug(cli_runner: CliRunner, caplog: Any) -> None:
    """Test enable debug."""
    result = cli_runner.invoke(__main__.main, f"--debug set --locale {TEST_LOCALE}")
    assert result.exit_code == 0
    assert __main__._WARNING_DEBUG_ENABLED in caplog.text


def test_log_no_folder(
    cli_runner: CliRunner, patch_root: Any, patch_datetime: Any
) -> None:
    """Test enable log."""
    assert not os.path.exists("logs")
    os.makedirs("logs")
    assert os.path.exists("logs")
    result = cli_runner.invoke(__main__.main, f"--log set --locale {TEST_LOCALE}")
    assert result.exit_code == 0

    with open("logs/2018-12-25.log") as myfile:
        assert __main__._WARNING_DEBUG_ENABLED in myfile.read()


def test_log_existing_folder(
    cli_runner: CliRunner, patch_root: Any, patch_datetime: Any
) -> None:
    """Test enable log."""
    assert not os.path.exists("logs")
    result = cli_runner.invoke(__main__.main, f"--log set --locale {TEST_LOCALE}")
    assert result.exit_code == 0

    with open("logs/2018-12-25.log") as myfile:
        assert __main__._WARNING_DEBUG_ENABLED in myfile.read()
