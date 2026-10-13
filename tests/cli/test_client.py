"""Test cases for the __main__ module."""

import os

from aiointercept import aiointercept
from click.testing import CliRunner
from syrupy.assertion import SnapshotAssertion

from tests import fixtures
from tests.const import TEST_GIGYA_URL
from tests.const import TEST_LOCALE
from tests.const import TEST_LOGIN_TOKEN
from tests.const import TEST_PASSWORD
from tests.const import TEST_PERSON_ID
from tests.const import TEST_USERNAME

from renault_api.cli import __main__
from renault_api.cli.renault_settings import CREDENTIAL_PATH
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential import JWTCredential
from renault_api.credential_store import FileCredentialStore
from renault_api.gigya import GIGYA_GMID
from renault_api.gigya import GIGYA_JWT
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.gigya import GIGYA_PERSON_ID
from renault_api.gigya import GIGYA_UCID


def test_login_prompt(
    mocked_responses: aiointercept, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_login(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        "login",
        input=f"{TEST_USERNAME}\n{TEST_PASSWORD}\n{TEST_LOCALE}\ny",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_login_no_prompt(
    mocked_responses: aiointercept, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_login(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        f"--locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_login_two_factor_auth(
    mocked_responses: aiointercept, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It prompts for the verification code, and saves the device ids."""
    fixtures.inject_gigya_tfa_all(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        f"--locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
        input="123456\n",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot

    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    assert credential_store.get_value(GIGYA_LOGIN_TOKEN) == TEST_LOGIN_TOKEN
    assert credential_store.get_value(GIGYA_GMID) == "sample-gmid"
    assert credential_store.get_value(GIGYA_UCID) == "sample-ucid"


def test_login_two_factor_auth_wrong_code(
    mocked_responses: aiointercept, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It prompts for the verification code again if it is wrong."""
    fixtures.inject_gigya_login_403101(mocked_responses)
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)
    fixtures.inject_gigya_tfa_emails(mocked_responses)
    fixtures.inject_gigya_tfa_send_email_code(mocked_responses)
    fixtures.inject_gigya_tfa_complete_email_verification(
        mocked_responses, "error/tfa_complete_email_verification.400006.json"
    )
    fixtures.inject_gigya_tfa_complete_email_verification(mocked_responses)
    fixtures.inject_gigya_tfa_finalize(mocked_responses)
    fixtures.inject_gigya_login(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        f"--locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
        input="000000\n123456\n",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_login_two_factor_auth_multiple_emails(
    mocked_responses: aiointercept, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It prompts for the email to send the verification code to."""
    fixtures.inject_gigya_login_403101(mocked_responses)
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)
    fixtures.inject_gigya_tfa_emails(mocked_responses, "tfa_get_emails.multiple.json")
    fixtures.inject_gigya_tfa_send_email_code(mocked_responses)
    fixtures.inject_gigya_tfa_complete_email_verification(mocked_responses)
    fixtures.inject_gigya_tfa_finalize(mocked_responses)
    fixtures.inject_gigya_login(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        f"--locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
        input="2\n123456\n",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot

    (request,) = fixtures.get_gigya_requests(
        mocked_responses, "accounts.tfa.email.sendVerificationCode"
    )
    assert request.query["emailID"] == "sample-email-id-2"


def test_login_two_factor_auth_no_email(
    mocked_responses: aiointercept, cli_runner: CliRunner
) -> None:
    """It fails if no email is registered for two-factor authentication."""
    fixtures.inject_gigya_login_403101(mocked_responses)
    fixtures.inject_gigya_tfa_bootstrap(mocked_responses)
    fixtures.inject_gigya_tfa_init(mocked_responses)
    fixtures.inject_gigya_tfa_emails(mocked_responses, "tfa_get_emails.empty.json")
    fixtures.inject_gigya_tfa_emails(mocked_responses, "tfa_get_emails.empty.json")

    result = cli_runner.invoke(
        __main__.main,
        f"--locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
    )
    assert result.exit_code == 1
    assert "No email address is registered" in result.output


def test_login_connection_error(
    mocked_responses: aiointercept, cli_runner: CliRunner
) -> None:
    """It reports connection errors without a traceback."""
    mocked_responses.post(f"{TEST_GIGYA_URL}/accounts.login", exception=True)

    result = cli_runner.invoke(
        __main__.main,
        f"--locale {TEST_LOCALE} "
        f"login --user {TEST_USERNAME} --password {TEST_PASSWORD}",
    )
    assert result.exit_code == 1
    assert "Error: Connection to Renault servers failed: " in result.output
    assert "Traceback" not in result.output


def test_list_accounts_prompt(
    mocked_responses: aiointercept, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    fixtures.inject_gigya_all(mocked_responses)
    fixtures.inject_get_person(mocked_responses)

    result = cli_runner.invoke(
        __main__.main,
        "accounts",
        input=f"{TEST_LOCALE}\nN\n{TEST_USERNAME}\n{TEST_PASSWORD}\n",
    )
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot


def test_list_accounts_no_prompt(
    mocked_responses: aiointercept, cli_runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """It exits with a status code of zero."""
    credential_store = FileCredentialStore(os.path.expanduser(CREDENTIAL_PATH))
    credential_store[CONF_LOCALE] = Credential(TEST_LOCALE)
    credential_store[GIGYA_LOGIN_TOKEN] = Credential(TEST_LOGIN_TOKEN)
    credential_store[GIGYA_PERSON_ID] = Credential(TEST_PERSON_ID)
    credential_store[GIGYA_JWT] = JWTCredential(fixtures.get_jwt())

    fixtures.inject_get_person(mocked_responses)

    result = cli_runner.invoke(__main__.main, "accounts")
    assert result.exit_code == 0, result.exception
    assert result.output == snapshot
