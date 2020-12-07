"""Test cases for the __main__ module."""
import pathlib
from typing import Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from click.testing import CliRunner

from renault_api.cli import __main__


@pytest.fixture
def runner(
    monkeypatch: MonkeyPatch, tmpdir: pathlib.Path
) -> Generator[CliRunner, None, None]:
    """Fixture for invoking command-line interfaces."""
    runner = CliRunner()

    monkeypatch.setattr("os.path.expanduser", lambda x: x.replace("~", str(tmpdir)))

    yield runner


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0, result.exception
