"""Test cases for the __main__ module."""

import pytest
from aioresponses import aioresponses
from aioresponses.core import RequestCall
from click.testing import CliRunner
from syrupy.assertion import SnapshotAssertion
from yarl import URL

from tests import fixtures

from . import initialise_credential_store
from renault_api.cli import __main__


def test_charge_battery_get_soc_levels(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    (fixtures.inject_get_vehicle_details(mocked_responses, "alpine_A290.1.json"),)
    fixtures.inject_get_charge_soc_levels(mocked_responses)

    result = cli_runner.invoke(__main__.main, "charge soclevels show")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


@pytest.mark.parametrize(
    ("min_level", "target_level", "exit_code"),
    [
        (20, 80, 0),  # Valid levels
        (15, 80, 0),  # Boundary valid levels
        (45, 100, 0),  # Boundary valid levels
        (14, 80, 2),  # Below minimum min level
        (46, 80, 2),  # Above maximum min level
        (20, 54, 2),  # Below minimum target level
        (20, 101, 2),  # Above maximum target level
        (22, 80, 2),  # Invalid step for min level
        (20, 77, 2),  # Invalid step for target level
    ],
)
def test_charge_battery_set_soc_levels(
    mocked_responses: aioresponses,
    cli_runner: CliRunner,
    snapshot: SnapshotAssertion,
    min_level: int,
    target_level: int,
    exit_code: int,
) -> None:
    """It exits with the proper status code and output."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "alpine_A290.1.json")
    url = fixtures.inject_set_charge_soc_levels(
        mocked_responses,
    )

    result = cli_runner.invoke(
        __main__.main,
        f"charge soclevels set --min {min_level} --target {target_level}",
    )
    assert result.exit_code == exit_code, result.exception

    if exit_code == 0:
        request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
        assert request.kwargs["json"] == snapshot

    assert result.output == snapshot


def test_charge_history_day(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_charge_history(
        mocked_responses, start="20201101", end="20201130", period="day"
    )

    result = cli_runner.invoke(
        __main__.main, "charge history --from 2020-11-01 --to 2020-11-30 --period day"
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_charge_history_month(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_charge_history(
        mocked_responses, start="202011", end="202011", period="month"
    )

    result = cli_runner.invoke(
        __main__.main, "charge history --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_charge_mode_get(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_charge_mode(mocked_responses)

    result = cli_runner.invoke(__main__.main, "charge mode")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_charge_mode_set(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    url = fixtures.inject_set_charge_mode(mocked_responses, mode="schedule_mode")

    result = cli_runner.invoke(__main__.main, "charge mode --set schedule_mode")
    assert result.exit_code == 0, result.exception

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_sessions_40(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_charges(mocked_responses, start="20201101", end="20201130")

    result = cli_runner.invoke(
        __main__.main, "charge sessions --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_sessions_45(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_charges(
        mocked_responses,
        start="20201101",
        end="20201130",
        filename="vehicle_data/charges-megane.json",
    )

    result = cli_runner.invoke(
        __main__.main, "charge sessions --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_sessions_50(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_50.1.json")
    fixtures.inject_get_charges(
        mocked_responses,
        start="20201101",
        end="20201130",
        filename="vehicle_data/charges-zoe_50.json",
    )

    result = cli_runner.invoke(
        __main__.main, "charge sessions --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_charge_schedule_show(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_charge_schedule(mocked_responses, "single")

    result = cli_runner.invoke(__main__.main, "charge schedule show")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


@pytest.mark.parametrize(
    "ev_schedule_type",
    [
        "single.active",
        "single.inactive",
        "multi.active",
    ],
)
def test_charge_schedule_show_alternate(
    mocked_responses: aioresponses,
    cli_runner: CliRunner,
    snapshot: SnapshotAssertion,
    ev_schedule_type: str,
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "renault_5.1.json")
    fixtures.inject_get_ev_settings(mocked_responses, ev_schedule_type)

    result = cli_runner.invoke(__main__.main, "charge schedule show")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_charging_settings_set(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_50.1.json")
    fixtures.inject_get_charging_settings(mocked_responses, "multi")
    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    monday = "--monday clear"
    friday = "--friday T23:30Z,480"
    saturday = "--saturday 19:30,120"
    result = cli_runner.invoke(
        __main__.main, f"charge schedule set 1 {monday} {friday} {saturday}"
    )
    assert result.exit_code == 0, result.exception
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_charging_settings_activate(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_50.1.json")
    fixtures.inject_get_charging_settings(mocked_responses, "multi")
    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    result = cli_runner.invoke(__main__.main, "charge schedule activate 3")
    assert result.exit_code == 0, result.exception
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]

    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_charging_settings_deactivate(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_50.1.json")
    fixtures.inject_get_charging_settings(mocked_responses, "multi")
    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    result = cli_runner.invoke(__main__.main, "charge schedule deactivate 1")
    assert result.exit_code == 0, result.exception
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]

    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_charging_start(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    url = fixtures.inject_set_charging_start(mocked_responses, "start")

    result = cli_runner.invoke(__main__.main, "charge start")
    assert result.exit_code == 0, result.exception

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_charging_stop(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    url = fixtures.inject_set_charging_start(mocked_responses, "stop")

    result = cli_runner.invoke(__main__.main, "charge stop")
    assert result.exit_code == 0, result.exception

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_charging_dacia_start(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "spring.1.json")
    url = fixtures.inject_set_kcm_charge_pause_resume(mocked_responses, "resume")

    result = cli_runner.invoke(__main__.main, "charge start")
    assert result.exit_code == 0, result.exception

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_charging_dacia_stop(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "spring.1.json")
    url = fixtures.inject_set_kcm_charge_pause_resume(mocked_responses, "pause")

    result = cli_runner.invoke(__main__.main, "charge stop")
    assert result.exit_code == 0, result.exception

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot
