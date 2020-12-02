"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from renault_api.cli import __main__
from renault_api.const import AVAILABLE_LOCALES


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main)
    assert result.exit_code == 0


@pytest.mark.skip()
@pytest.mark.parametrize("locale", AVAILABLE_LOCALES.keys())
def test_get_keys_succeeds(runner: CliRunner, locale: str) -> None:
    """It exits with a status code of zero."""
    runner.invoke(__main__.set, ["--locale", locale])
    result = runner.invoke(__main__.get_keys)
    assert result.exit_code == 0
    expected_output = f"Current locale: {locale}\n"
    "Current gigya-api-key: None\n"
    "Current gigya-api-url: None\n"
    "Current kamereon-api-key: None\n"
    "Current kamereon-api-url: None\n"
    assert result.output == expected_output
