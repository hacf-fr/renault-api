"""Test cases for the __main__ module."""
from aioresponses import aioresponses
from aioresponses.core import RequestCall
from click.testing import CliRunner
from tests import fixtures
from yarl import URL

from . import initialise_credential_store
from renault_api.cli import __main__


def test_charge_history_day(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charge_history(
        mocked_responses, start="20201101", end="20201130", period="day"
    )

    result = cli_runner.invoke(
        __main__.main, "charge history --from 2020-11-01 --to 2020-11-30 --period day"
    )
    assert result.exit_code == 0, result.exception

    expected_output = (
        "     Day    Number of charges  Total time charging      Errors\n"
        "--------  -------------------  ---------------------  --------\n"
        "20201208                    2  8:15:00                       0\n"
        "20201205                    1  10:57:00                      0\n"
    )
    assert expected_output == result.output


def test_charge_history_month(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charge_history(
        mocked_responses, start="202011", end="202011", period="month"
    )

    result = cli_runner.invoke(
        __main__.main, "charge history --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception

    expected_output = (
        "  Month    Number of charges  Total time charging      Errors\n"
        "-------  -------------------  ---------------------  --------\n"
        " 202011                    1  7:59:00                       0\n"
    )
    assert expected_output == result.output


def test_charge_mode_get(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charge_mode(mocked_responses)

    result = cli_runner.invoke(__main__.main, "charge mode")
    assert result.exit_code == 0, result.exception

    expected_output = "Charge mode: always\n"
    assert expected_output == result.output


def test_charge_mode_set(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    url = fixtures.inject_set_charge_mode(mocked_responses, mode="schedule_mode")

    result = cli_runner.invoke(__main__.main, "charge mode --set schedule_mode")
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {"attributes": {"action": "schedule_mode"}, "type": "ChargeMode"}
    }
    expected_output = "{'action': 'schedule_mode'}\n"

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert expected_output == result.output


def test_sessions(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charges(mocked_responses, start="20201101", end="20201130")

    result = cli_runner.invoke(
        __main__.main, "charge sessions --from 2020-11-01 --to 2020-11-30"
    )
    assert result.exit_code == 0, result.exception

    expected_output = (
        "Charge start         Charge end           Duration    Power (kW)  "
        "  Started at    Finished at    Charge gained    Power level    Status\n"
        "-------------------  -------------------  ----------  ------------"
        "  ------------  -------------  ---------------  -------------  --------\n"
        "2020-11-11 01:31:03  2020-11-11 09:30:17  7:59:00     3.10 kW     "
        "  15 %          74 %           59 %             slow           ok\n"
    )
    assert expected_output == result.output


def test_charge_schedule_show(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charging_settings(mocked_responses, "multi")

    result = cli_runner.invoke(__main__.main, "charge schedule show")
    assert result.exit_code == 0, result.exception

    expected_output = (
        "Mode: scheduled\n"
        "\n"
        "Schedule ID: 1 [Active]\n"
        "Day        Start time    End time    Duration\n"
        "---------  ------------  ----------  ----------\n"
        "Monday     01:00         08:30       7:30:00\n"
        "Tuesday    01:00         08:30       7:30:00\n"
        "Wednesday  01:00         08:30       7:30:00\n"
        "Thursday   01:00         08:30       7:30:00\n"
        "Friday     01:00         08:30       7:30:00\n"
        "Saturday   01:00         08:30       7:30:00\n"
        "Sunday     01:00         08:30       7:30:00\n"
        "\n"
        "Schedule ID: 2 [Active]\n"
        "Day        Start time    End time    Duration\n"
        "---------  ------------  ----------  ----------\n"
        "Monday     00:30         00:45       0:15:00\n"
        "Tuesday    00:30         00:45       0:15:00\n"
        "Wednesday  00:30         00:45       0:15:00\n"
        "Thursday   00:30         00:45       0:15:00\n"
        "Friday     00:30         00:45       0:15:00\n"
        "Saturday   00:30         00:45       0:15:00\n"
        "Sunday     00:30         00:45       0:15:00\n"
        "\n"
        "Schedule ID: 3\n"
        "Day        Start time    End time    Duration\n"
        "---------  ------------  ----------  ----------\n"
        "Monday     -             -           -\n"
        "Tuesday    -             -           -\n"
        "Wednesday  -             -           -\n"
        "Thursday   -             -           -\n"
        "Friday     -             -           -\n"
        "Saturday   -             -           -\n"
        "Sunday     -             -           -\n"
        "\n"
        "Schedule ID: 4\n"
        "Day        Start time    End time    Duration\n"
        "---------  ------------  ----------  ----------\n"
        "Monday     -             -           -\n"
        "Tuesday    -             -           -\n"
        "Wednesday  -             -           -\n"
        "Thursday   -             -           -\n"
        "Friday     -             -           -\n"
        "Saturday   -             -           -\n"
        "Sunday     -             -           -\n"
        "\n"
        "Schedule ID: 5\n"
        "Day        Start time    End time    Duration\n"
        "---------  ------------  ----------  ----------\n"
        "Monday     -             -           -\n"
        "Tuesday    -             -           -\n"
        "Wednesday  -             -           -\n"
        "Thursday   -             -           -\n"
        "Friday     -             -           -\n"
        "Saturday   -             -           -\n"
        "Sunday     -             -           -\n"
    )
    assert expected_output == result.output


def test_charging_settings_set(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charging_settings(mocked_responses, "multi")
    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    monday = "--monday clear"
    friday = "--friday T23:30Z,480"
    saturday = "--saturday 19:30,120"
    result = cli_runner.invoke(
        __main__.main, f"charge schedule set 1 {monday} {friday} {saturday}"
    )
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {
                "schedules": [
                    {
                        "id": 1,
                        "activated": True,
                        "monday": None,
                        "tuesday": {"startTime": "T00:00Z", "duration": 450},
                        "wednesday": {"startTime": "T00:00Z", "duration": 450},
                        "thursday": {"startTime": "T00:00Z", "duration": 450},
                        "friday": {"startTime": "T23:30Z", "duration": 480},
                        "saturday": {"startTime": "T18:30Z", "duration": 120},
                        "sunday": {"startTime": "T00:00Z", "duration": 450},
                    },
                    {
                        "id": 2,
                        "activated": True,
                        "monday": {"startTime": "T23:30Z", "duration": 15},
                        "tuesday": {"startTime": "T23:30Z", "duration": 15},
                        "wednesday": {"startTime": "T23:30Z", "duration": 15},
                        "thursday": {"startTime": "T23:30Z", "duration": 15},
                        "friday": {"startTime": "T23:30Z", "duration": 15},
                        "saturday": {"startTime": "T23:30Z", "duration": 15},
                        "sunday": {"startTime": "T23:30Z", "duration": 15},
                    },
                    {
                        "id": 3,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                    {
                        "id": 4,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                    {
                        "id": 5,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                ],
            },
            "type": "ChargeSchedule",
        }
    }
    expected_output = "{'schedules': [{'id': 1, 'activated': True, "
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert result.output.startswith(expected_output)


def test_charging_settings_activate(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charging_settings(mocked_responses, "multi")
    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    result = cli_runner.invoke(__main__.main, "charge schedule activate 3")
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {
                "schedules": [
                    {
                        "id": 1,
                        "activated": True,
                        "monday": {"startTime": "T00:00Z", "duration": 450},
                        "tuesday": {"startTime": "T00:00Z", "duration": 450},
                        "wednesday": {"startTime": "T00:00Z", "duration": 450},
                        "thursday": {"startTime": "T00:00Z", "duration": 450},
                        "friday": {"startTime": "T00:00Z", "duration": 450},
                        "saturday": {"startTime": "T00:00Z", "duration": 450},
                        "sunday": {"startTime": "T00:00Z", "duration": 450},
                    },
                    {
                        "id": 2,
                        "activated": True,
                        "monday": {"startTime": "T23:30Z", "duration": 15},
                        "tuesday": {"startTime": "T23:30Z", "duration": 15},
                        "wednesday": {"startTime": "T23:30Z", "duration": 15},
                        "thursday": {"startTime": "T23:30Z", "duration": 15},
                        "friday": {"startTime": "T23:30Z", "duration": 15},
                        "saturday": {"startTime": "T23:30Z", "duration": 15},
                        "sunday": {"startTime": "T23:30Z", "duration": 15},
                    },
                    {
                        "id": 3,
                        "activated": True,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                    {
                        "id": 4,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                    {
                        "id": 5,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                ]
            },
            "type": "ChargeSchedule",
        }
    }
    expected_output = "{'schedules': [{'id': 1, 'activated': True, "

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]

    assert expected_json == request.kwargs["json"]
    assert result.output.startswith(expected_output)


def test_charging_settings_deactivate(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)
    fixtures.inject_get_charging_settings(mocked_responses, "multi")
    url = fixtures.inject_set_charge_schedule(mocked_responses, "schedules")

    result = cli_runner.invoke(__main__.main, "charge schedule deactivate 1")
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {
                "schedules": [
                    {
                        "id": 1,
                        "activated": False,
                        "monday": {"startTime": "T00:00Z", "duration": 450},
                        "tuesday": {"startTime": "T00:00Z", "duration": 450},
                        "wednesday": {"startTime": "T00:00Z", "duration": 450},
                        "thursday": {"startTime": "T00:00Z", "duration": 450},
                        "friday": {"startTime": "T00:00Z", "duration": 450},
                        "saturday": {"startTime": "T00:00Z", "duration": 450},
                        "sunday": {"startTime": "T00:00Z", "duration": 450},
                    },
                    {
                        "id": 2,
                        "activated": True,
                        "monday": {"startTime": "T23:30Z", "duration": 15},
                        "tuesday": {"startTime": "T23:30Z", "duration": 15},
                        "wednesday": {"startTime": "T23:30Z", "duration": 15},
                        "thursday": {"startTime": "T23:30Z", "duration": 15},
                        "friday": {"startTime": "T23:30Z", "duration": 15},
                        "saturday": {"startTime": "T23:30Z", "duration": 15},
                        "sunday": {"startTime": "T23:30Z", "duration": 15},
                    },
                    {
                        "id": 3,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                    {
                        "id": 4,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                    {
                        "id": 5,
                        "activated": False,
                        "monday": None,
                        "tuesday": None,
                        "wednesday": None,
                        "thursday": None,
                        "friday": None,
                        "saturday": None,
                        "sunday": None,
                    },
                ]
            },
            "type": "ChargeSchedule",
        }
    }
    expected_output = "{'schedules': [{'id': 1, 'activated': True, "

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]

    assert expected_json == request.kwargs["json"]
    assert result.output.startswith(expected_output)


def test_charging_start(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)

    # RENAULT
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    url = fixtures.inject_set_charging_start(mocked_responses, "start")

    result = cli_runner.invoke(__main__.main, "charge start")
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {"action": "start"},
            "type": "ChargingStart",
        }
    }
    expected_output = "{'action': 'start'}\n"
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert expected_output == result.output


def test_charging_renault_stop(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)

    # RENAULT
    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_set_charge_pause_resume(mocked_responses, "pause")

    result = cli_runner.invoke(__main__.main, "charge stop")
    assert result.exit_code == 1, result.exception


def test_charging_dacia_start(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)

    # DACIA
    fixtures.inject_get_vehicle_details(mocked_responses, "spring.1.json")
    url = fixtures.inject_set_charge_pause_resume(mocked_responses, "resume")

    result = cli_runner.invoke(__main__.main, "charge start")
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {"action": "resume"},
            "type": "ChargePauseResume",
        }
    }
    expected_output = "{'action': 'resume'}\n"
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert expected_output == result.output


def test_charging_dacia_stop(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    initialise_credential_store(include_account_id=True, include_vin=True)

    # DACIA
    fixtures.inject_get_vehicle_details(mocked_responses, "spring.1.json")
    url = fixtures.inject_set_charge_pause_resume(mocked_responses, "pause")

    result = cli_runner.invoke(__main__.main, "charge stop")
    assert result.exit_code == 0, result.exception

    expected_json = {
        "data": {
            "attributes": {"action": "pause"},
            "type": "ChargePauseResume",
        }
    }
    expected_output = "{'action': 'pause'}\n"
    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
    assert expected_output == result.output
