"""Test cases for the __main__ module."""
import os
import pathlib
from typing import Generator

import pytest
from click.testing import CliRunner
from tests.const import TEST_LOCALE

from renault_api.cli import __main__


@pytest.fixture(scope="function")
def temp_root(tmpdir: pathlib.Path) -> Generator[pathlib.Path, None, None]:
    """Update current directory to test log folder."""
    root_dir = os.getcwd()
    os.chdir(tmpdir)
    yield tmpdir
    os.chdir(root_dir)


def test_main_succeeds(cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = cli_runner.invoke(__main__.main)
    assert result.exit_code == 0, result.exception


def test_debug(cli_runner: CliRunner) -> None:
    """Test enable debug."""
    result = cli_runner.invoke(__main__.main, f"--debug set --locale {TEST_LOCALE}")
    assert result.exit_code == 0


def test_log_no_folder(cli_runner: CliRunner, temp_root: str) -> None:
    """Test enable log."""
    assert not os.path.exists("logs")
    os.makedirs("logs")
    assert os.path.exists("logs")
    result = cli_runner.invoke(__main__.main, f"--log set --locale {TEST_LOCALE}")
    assert result.exit_code == 0


def test_log_existing_folder(cli_runner: CliRunner, temp_root: str) -> None:
    """Test enable log."""
    cli_runner.isolated_filesystem()
    assert not os.path.exists("logs")
    result = cli_runner.invoke(__main__.main, f"--log set --locale {TEST_LOCALE}")
    assert result.exit_code == 0
