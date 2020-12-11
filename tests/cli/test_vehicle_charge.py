"""Test cases for the __main__ module."""
from aioresponses import aioresponses
from click.testing import CliRunner
from tests import fixtures

from . import initialise_credential_store
from renault_api.cli import __main__

EXPECTED_CHARGES = (
    "Charge start         Charge end           Duration    Power (kW)  "
    "  Started at    Finished at    Charge gained    Power level    Status\n"
    "-------------------  -------------------  ----------  ------------"
    "  ------------  -------------  ---------------  -------------  --------\n"
    "2020-11-11 01:31:03  2020-11-11 09:30:17  7:59:00     3.10 kW     "
    "  15 %          74 %           59 %             slow           ok\n"
)
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


def test_vehicle_charges(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_kamereon_charges(mocked_responses, start="20201101", end="20201130")

    result = cli_runner.invoke(
        __main__.main, "charges --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_CHARGES == result.output


def test_vehicle_charge_history_month(
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


def test_vehicle_charge_history_day(
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
