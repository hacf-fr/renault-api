"""Test cases for the __main__ module."""
import os
from locale import getdefaultlocale

import pytest
from aioresponses import aioresponses
from click.testing import CliRunner
from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_LOCALE
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME
from tests.const import TEST_VIN

from renault_api.cli import __main__
from renault_api.cli.renault_settings import CONF_ACCOUNT_ID
from renault_api.cli.renault_settings import CONF_VIN
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import FileCredentialStore
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya import GIGYA_PERSON_ID

EXPECTED_STATUS = {
    "captur_ii.1.json": (
        "----------------  -------------------\n"
        "Total mileage     49114.27 km\n"
        "GPS Latitude      48.1234567\n"
        "GPS Longitude     11.1234567\n"
        "GPS last updated  2020-02-18 17:58:38\n"
        "----------------  -------------------\n"
    ),
    "twingo_ze.1.json": (
        "----------------  -------------------------\n"
        "Battery level     50 %\n"
        "Last updated      2020-11-17 09:06:48\n"
        "Range estimate    128 km\n"
        "Plug state        PlugState.UNPLUGGED\n"
        "Charging state    ChargeState.NOT_IN_CHARGE\n"
        "Charge mode       always\n"
        "Total mileage     49114.27 km\n"
        "GPS Latitude      48.1234567\n"
        "GPS Longitude     11.1234567\n"
        "GPS last updated  2020-02-18 17:58:38\n"
        "----------------  -------------------------\n"
    ),
    "zoe_40.1.json": (
        "--------------------  -------------------------\n"
        "Battery level         50 %\n"
        "Last updated          2020-11-17 09:06:48\n"
        "Range estimate        128 km\n"
        "Plug state            PlugState.UNPLUGGED\n"
        "Charging state        ChargeState.NOT_IN_CHARGE\n"
        "Charge mode           always\n"
        "Total mileage         49114.27 km\n"
        "HVAC status           off\n"
        "External temperature  8.0 °C\n"
        "--------------------  -------------------------\n"
    ),
    "zoe_40.2.json": (
        "--------------------  -------------------------\n"
        "Battery level         50 %\n"
        "Last updated          2020-11-17 09:06:48\n"
        "Range estimate        128 km\n"
        "Plug state            PlugState.UNPLUGGED\n"
        "Charging state        ChargeState.NOT_IN_CHARGE\n"
        "Charge mode           always\n"
        "Total mileage         49114.27 km\n"
        "HVAC status           off\n"
        "External temperature  8.0 °C\n"
        "--------------------  -------------------------\n"
    ),
    "zoe_50.1.json": (
        "----------------  -------------------------\n"
        "Battery level     50 %\n"
        "Last updated      2020-11-17 09:06:48\n"
        "Range estimate    128 km\n"
        "Plug state        PlugState.UNPLUGGED\n"
        "Charging state    ChargeState.NOT_IN_CHARGE\n"
        "Charge mode       always\n"
        "Total mileage     49114.27 km\n"
        "GPS Latitude      48.1234567\n"
        "GPS Longitude     11.1234567\n"
        "GPS last updated  2020-02-18 17:58:38\n"
        "----------------  -------------------------\n"
    ),
}


def test_vehicle_details(mocked_responses: aioresponses, cli_runner: CliRunner) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")

    result = cli_runner.invoke(__main__.main, "vehicle")
    assert result.exit_code == 0, result.exception

    expected_output = (
        "Registration    Brand    Model    VIN\n"
        "--------------  -------  -------  -----------------\n"
        "REG-NUMBER      RENAULT  ZOE      VF1AAAAA555777999\n"
    )
    assert expected_output == result.output


@pytest.mark.parametrize(
    "filename", fixtures.get_json_files(f"{fixtures.KAMEREON_FIXTURE_PATH}/vehicles")
)
def test_vehicle_status(
    mocked_responses: aioresponses, cli_runner: CliRunner, filename: str
) -> None:
    """It exits with a status code of zero."""
    filename = os.path.basename(filename)
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_details(mocked_responses, filename)
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.2.json")
    fixtures.inject_vehicle_status(mocked_responses)

    result = cli_runner.invoke(__main__.main, "status")
    assert result.exit_code == 0, result.exception

    assert EXPECTED_STATUS[filename] == result.output


def test_vehicle_status_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_all(mocked_responses)
    fixtures.inject_get_person(mocked_responses)

    # Injected for account selection
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")
    vehicle2_urlpath = f"accounts/account-id-2/vehicles?{fixtures.DEFAULT_QUERY_STRING}"
    fixtures.inject_data(
        mocked_responses,
        vehicle2_urlpath,
        "vehicles/zoe_40.1.json",
    )

    # Injected again for vehicle selection
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")

    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.2.json")
    fixtures.inject_vehicle_status(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        "status",
        input=f"{TEST_LOCALE}\nN\n{TEST_USERNAME}\n{TEST_PASSWORD}\n1\ny\n1\ny\n",
    )
    assert result.exit_code == 0, result.exception

    expected_output = (
        f"Please select a locale [{getdefaultlocale()[0]}]: {TEST_LOCALE}\n"
        "Do you want to save the locale to the credential store? [y/N]: N\n"
        "\n"
        f"User: {TEST_USERNAME}\n"
        "Password: \n"
        "\n"
        "    ID            Type         Vehicles\n"
        "--  ------------  ---------  ----------\n"
        " 1  account-id-1  MYRENAULT           1\n"
        " 2  account-id-2  SFDC                1\n"
        "\n"
        "Please select account [1]: 1\n"
        "Do you want to save the account ID to the credential store? [y/N]: y\n"
        "\n"
        "    Vin                Registration    Brand    Model\n"
        "--  -----------------  --------------  -------  -------\n"
        " 1  VF1AAAAA555777999  REG-NUMBER      RENAULT  ZOE\n"
        "\n"
        "Please select vehicle [1]: 1\n"
        "Do you want to save the VIN to the credential store? [y/N]: y\n"
        "\n"
        f"{EXPECTED_STATUS['zoe_40.1.json']}"
    )
    assert expected_output == result.output


def test_vehicle_status_no_prompt(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_details(mocked_responses, "zoe_40.1.json")
    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.2.json")
    fixtures.inject_vehicle_status(mocked_responses)

    result = cli_runner.invoke(
        __main__.main, f"--account {TEST_ACCOUNT_ID} --vin {TEST_VIN} status"
    )
    assert result.exit_code == 0, result.exception

    assert EXPECTED_STATUS["zoe_40.1.json"] == result.output


def test_vehicle_contracts(
    mocked_responses: aioresponses, cli_runner: CliRunner
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[CONF_ACCOUNT_ID] = Credential(TEST_ACCOUNT_ID)
    credential_store[CONF_VIN] = Credential(TEST_VIN)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_vehicle_contracts(mocked_responses, "fr_FR.1.json")

    result = cli_runner.invoke(__main__.main, "contracts")
    assert result.exit_code == 0, result.exception

    expected_output = (
        "Type                            Code                  "
        "Description                       Start       End         Status\n"
        "------------------------------  --------------------  "
        "--------------------------------  ----------  ----------  "
        "------------------\n"
        "WARRANTY_MAINTENANCE_CONTRACTS  40                    "
        "CONTRAT LOSANGE                   2018-04-04  2022-04-03  Actif\n"
        "CONNECTED_SERVICES              ZECONNECTP            "
        "My Z.E. Connect en série 36 mois  2018-08-23  2021-08-23  Actif\n"
        "CONNECTED_SERVICES              GBA                   "
        "Battery Services                  2018-03-23              "
        "Echec d’activation\n"
        "WARRANTY                        ManufacturerWarranty  "
        "Garantie fabricant                            2020-04-03  Expiré\n"
        "WARRANTY                        PaintingWarranty      "
        "Garantie peinture                             2021-04-03  Actif\n"
        "WARRANTY                        CorrosionWarranty     "
        "Garantie corrosion                            2030-04-03  Actif\n"
        "WARRANTY                        GMPeWarranty          "
        "Garantie GMPe                                 2020-04-03  Expiré\n"
        "WARRANTY                        AssistanceWarranty    "
        "Garantie assistance                           2020-04-03  Expiré\n"
    )
    assert expected_output == result.output
