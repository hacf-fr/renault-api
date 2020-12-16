"""Test cases for the __main__ module."""
from aioresponses import aioresponses
from aioresponses.core import RequestCall  # type:ignore
from click.testing import CliRunner
from tests import fixtures
from yarl import URL

from . import initialise_credential_store
from renault_api.cli import __main__


def test_hvac_history_day(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_hvac_history(
        mocked_responses, start="20201101", end="20201130", period="day"
    )

    result = cli_runner.invoke(
        __main__.main, "hvac history --from 2020-11-01 --to 2020-11-30 --period day"
    )
    assert result.exit_code == 0, result.exception

    expected_output = "{}\n"
    assert expected_output == result.output


def test_hvac_history_month(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_hvac_history(
        mocked_responses, start="202011", end="202011", period="month"
    )

    result = cli_runner.invoke(
        __main__.main, "hvac history --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception

    expected_output = "{}\n"
    assert expected_output == result.output


def test_hvac_cancel(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    url = fixtures.inject_set_hvac_start(mocked_responses, result="cancel")

    result = cli_runner.invoke(__main__.main, "hvac cancel")
    assert result.exit_code == 0, result.exception

    expected_json = {"data": {"attributes": {"action": "cancel"}, "type": "HvacStart"}}
    expected_output = "{'action': 'cancel'}\n"

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert expected_output == result.output


def test_sessions(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_hvac_sessions(
        mocked_responses, start="20201101", end="20201130"
    )

    result = cli_runner.invoke(
        __main__.main, "hvac sessions --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception

    expected_output = "{}\n"
    assert expected_output == result.output


def test_hvac_start_now(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    url = fixtures.inject_set_hvac_start(mocked_responses, "start")

    result = cli_runner.invoke(__main__.main, "hvac start --temperature 25")
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {"action": "start", "targetTemperature": 25},
            "type": "HvacStart",
        }
    }
    expected_output = "{'action': 'start', 'targetTemperature': 21.0}\n"
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert expected_output == result.output


def test_hvac_start_later(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    url = fixtures.inject_set_hvac_start(mocked_responses, "start")

    result = cli_runner.invoke(
        __main__.main, "hvac start --temperature 24 --at '2020-12-25 at 11:50'"
    )
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {
                "action": "start",
                "startDateTime": "2020-12-25T10:50:00Z",
                "targetTemperature": 24,
            },
            "type": "HvacStart",
        }
    }
    expected_output = "{'action': 'start', 'targetTemperature': 21.0}\n"
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert expected_output == result.output
