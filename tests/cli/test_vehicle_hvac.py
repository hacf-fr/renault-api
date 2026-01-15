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


def test_hvac_history_day(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
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
    assert result.output == snapshot


def test_hvac_history_month(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
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
    assert result.output == snapshot


@pytest.mark.parametrize(
    ("vehicle_fixture", "action"),
    [("zoe_40.1.json", "cancel"), ("alpine_A290.1.json", "stop")],
)
def test_hvac_cancel(
    mocked_responses: aioresponses,
    cli_runner: CliRunner,
    snapshot: SnapshotAssertion,
    vehicle_fixture: str,
    action: str,
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    url = fixtures.inject_set_hvac_start(mocked_responses, result=action)
    fixtures.inject_get_vehicle_details(mocked_responses, vehicle_fixture)

    result = cli_runner.invoke(__main__.main, "hvac cancel")
    assert result.exit_code == 0, result.exception

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_sessions(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_hvac_sessions(
        mocked_responses, start="20201101", end="20201130"
    )

    result = cli_runner.invoke(
        __main__.main, "hvac sessions --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_hvac_start_now(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    url = fixtures.inject_set_hvac_start(mocked_responses, "start")

    result = cli_runner.invoke(__main__.main, "hvac start --temperature 25")
    assert result.exit_code == 0, result.exception
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot


def test_hvac_start_later(
    mocked_responses: aioresponses, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    url = fixtures.inject_set_hvac_start(mocked_responses, "start")

    result = cli_runner.invoke(
        __main__.main, "hvac start --temperature 24 --at '2020-12-25T11:50:00+02:00'"
    )
    assert result.exit_code == 0, result.exception
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert request.kwargs["json"] == snapshot
    assert result.output == snapshot
