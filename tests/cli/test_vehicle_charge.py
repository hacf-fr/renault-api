"""Test cases for the __main__ module."""
from aioresponses import aioresponses
from click.testing import CliRunner
from tests import fixtures

from . import initialise_credential_store
from renault_api.cli import __main__

EXPECTED_CHARGE_HISTORY_DAY = (
    "     Day    Number of charges  Total time charging      Errors\n"
    "--------  -------------------  ---------------------  --------\n"
    "20201208                    2  8:15:00                       0\n"
    "20201205                    1  10:57:00                      0\n"
)
EXPECTED_CHARGE_HISTORY_MONTH = (
    "  Month    Number of charges  Total time charging      Errors\n"
    "-------  -------------------  ---------------------  --------\n"
    " 202011                    1  7:59:00                       0\n"
)
EXPECTED_CHARGE_MODE_GET = "Charge mode: always\n"
EXPECTED_CHARGE_MODE_SET = "{'action': 'schedule_mode'}\n"
EXPECTED_CHARGES = (
    "Charge start         Charge end           Duration    Power (kW)  "
    "  Started at    Finished at    Charge gained    Power level    Status\n"
    "-------------------  -------------------  ----------  ------------"
    "  ------------  -------------  ---------------  -------------  --------\n"
    "2020-11-11 01:31:03  2020-11-11 09:30:17  7:59:00     3.10 kW     "
    "  15 %          74 %           59 %             slow           ok\n"
)
EXPECTED_CHARGING_START = "{'action': 'start'}\n"
EXPECTED_CHARGING_SETTINGS_GET = (
    "Mode: scheduled\n"
    "Schedule ID: 1 [Active]\n"
    "Day        Start time    End time    Duration\n"
    "---------  ------------  ----------  ----------\n"
    "Monday     13:00         13:15       0:15:00\n"
    "Tuesday    05:30         12:30       7:00:00\n"
    "Wednesday  23:30         06:30       7:00:00\n"
    "Thursday   23:00         06:00       7:00:00\n"
    "Friday     13:15         13:30       0:15:00\n"
    "Saturday   13:30         14:00       0:30:00\n"
    "Sunday     13:45         14:30       0:45:00\n"
)
EXPECTED_CHARGING_SETTINGS_SET = (
    "{'schedules': [{'id': 1, 'activated': True, "
    "'monday': {'startTime': 'T12:00Z', 'duration': 15}, "
    "'tuesday': {'startTime': 'T04:30Z', 'duration': 420}, "
    "'wednesday': {'startTime': 'T22:30Z', 'duration': 420}, "
    "'thursday': {'startTime': 'T22:00Z', 'duration': 420}, "
    "'friday': {'startTime': 'T23:30Z', 'duration': 480}, "
    "'saturday': {'startTime': 'T18:30Z', 'duration': 120}, "
    "'sunday': {'startTime': 'T12:45Z', 'duration': 45}}]}\n"
)


def test_charge_history_day(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_charge_history(
        mocked_responses, start="20201101", end="20201130", period="day"
    )

    result = cli_runner.invoke(
        __main__.main, "charge-history --from 2020-11-01 --to 2020-11-30 --period day"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGE_HISTORY_DAY == result.output


def test_charge_history_month(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_charge_history(
        mocked_responses, start="202011", end="202011", period="month"
    )

    result = cli_runner.invoke(
        __main__.main, "charge-history --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGE_HISTORY_MONTH == result.output


def test_charge_mode_get(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_charge_mode(mocked_responses)

    result = cli_runner.invoke(__main__.main, "charge-mode")
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGE_MODE_GET == result.output


def test_charge_mode_set(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_action_charge_mode(mocked_responses, mode="schedule_mode")

    result = cli_runner.invoke(__main__.main, "charge-mode --mode schedule_mode")
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGE_MODE_SET == result.output


def test_charges(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_charges(mocked_responses, start="20201101", end="20201130")

    result = cli_runner.invoke(
        __main__.main, "charges --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGES == result.output


def test_charging_settings_get(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_charging_settings(mocked_responses)

    result = cli_runner.invoke(__main__.main, "charging-settings --id 1")
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGING_SETTINGS_GET == result.output


def test_charging_settings_set(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_charging_settings(mocked_responses)
    fixtures.inject_kamereon_action_charge_schedule(mocked_responses)

    friday = "--friday T23:30Z,480"
    saturday = "--saturday 19:30,120"
    result = cli_runner.invoke(
        __main__.main, f"charging-settings --id 1 --set {friday} {saturday}"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGING_SETTINGS_SET == result.output


def test_charging_start(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_action_charging_start(mocked_responses)

    result = cli_runner.invoke(__main__.main, "charging-start")
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGING_START == result.output
