"""Test cases for the __main__ module."""

import pytest
from aioresponses import aioresponses
from click.testing import CliRunner
from syrupy.assertion import SnapshotAssertion

from tests import fixtures

from . import initialise_credential_store
from renault_api.cli import __main__


@pytest.mark.parametrize(
    "type",
    [
        "lights",
        "horn"
    ],
)
def test_hornlights_start(
    mocked_responses: aioresponses,
    cli_runner: CliRunner,
    snapshot: SnapshotAssertion,
    type: str,
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_vehicle_details(mocked_responses, "alpine_A290.1.json")
    fixtures.inject_start_hornlight(mocked_responses, type=type)

    result = cli_runner.invoke(
        __main__.main, f"hornlights {type}"
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot
