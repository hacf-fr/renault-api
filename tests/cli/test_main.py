"""Test cases for the __main__ module."""
from click.testing import CliRunner

from renault_api.cli import __main__


def test_main_succeeds(cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = cli_runner.invoke(__main__.main)
    assert result.exit_code == 0, result.exception
