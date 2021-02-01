"""Singletons for the CLI."""
import json
from locale import getdefaultlocale
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click
from tabulate import tabulate

from renault_api.cli import renault_account
from renault_api.cli import renault_vehicle
from renault_api.const import CONF_LOCALE
from renault_api.credential import Credential
from renault_api.credential_store import CredentialStore
from renault_api.exceptions import RenaultException
from renault_api.gigya import GIGYA_LOGIN_TOKEN
from renault_api.helpers import get_api_keys
from renault_api.renault_client import RenaultClient
from renault_api.renault_session import RenaultSession


async def get_locale(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> str:
    """Prompt the user for locale."""
    credential_store: CredentialStore = ctx_data["credential_store"]
    locale = credential_store.get_value(CONF_LOCALE)
    if locale:
        return locale

    default_locale = getdefaultlocale()[0]
    while True:
        locale = click.prompt("Please select a locale", default=default_locale)
        if locale:  # pragma: no branch
            try:
                await get_api_keys(locale, websession=websession)
            except RenaultException as exc:  # pragma: no cover
                click.echo(f"Locale `{locale}` is unknown: {exc}", err=True)
            else:
                if click.confirm(
                    "Do you want to save the locale to the credential store?",
                    default=False,
                ):
                    credential_store[CONF_LOCALE] = Credential(locale)
                # Add blank new line
                click.echo("")
                return locale


async def _create_renault_session(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultSession:
    """Get RenaultClient for use by CLI."""
    credential_store: CredentialStore = ctx_data["credential_store"]
    locale = ctx_data.get("locale")
    if not locale:
        locale = await get_locale(websession, ctx_data)

    country = locale[-2:]
    locale_details = await get_api_keys(locale=locale, websession=websession)
    return RenaultSession(
        websession=websession,
        locale=locale,
        country=country,
        locale_details=locale_details,
        credential_store=credential_store,
    )


async def _get_logged_in_session(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultSession:
    """Get RenaultSession for use by CLI."""
    session = await _create_renault_session(websession=websession, ctx_data=ctx_data)

    credential_store: CredentialStore = ctx_data["credential_store"]
    if GIGYA_LOGIN_TOKEN not in credential_store:
        await _prompt_login(session)
    return session


async def get_logged_in_client(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> RenaultClient:
    """Get RenaultClient for use by CLI."""
    session = await _get_logged_in_session(websession=websession, ctx_data=ctx_data)
    return RenaultClient(session=session)


async def _prompt_login(session: RenaultSession) -> None:
    """Prompt the user for credentials."""
    while True:
        user = click.prompt("User")
        password = click.prompt("Password", hide_input=True)
        try:
            await session.login(user, password)
        except RenaultException as exc:  # pragma: no cover
            click.echo(f"Login failed: {exc}.", err=True)
        else:
            # Add blank new line
            click.echo("")
            return


async def login(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    user: str,
    password: str,
) -> None:
    """Attempt login."""
    session = await _create_renault_session(websession=websession, ctx_data=ctx_data)
    await session.login(user, password)


async def display_accounts(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any]
) -> None:
    """Display accounts."""
    client = await get_logged_in_client(websession=websession, ctx_data=ctx_data)
    response = await client.get_person()
    if response.accounts is None:  # pragma: no cover
        raise ValueError("response.accounts is None")
    accounts = {account.accountType: account.accountId for account in response.accounts}
    click.echo(tabulate(accounts.items(), headers=["Type", "ID"]))


async def http_get_endpoint(
    websession: aiohttp.ClientSession, ctx_data: Dict[str, Any], endpoint: str
) -> str:
    """Run HTTP GET request."""
    if "{account_id}" in endpoint:  # pragma: no branch
        account = await renault_account.get_account(
            websession=websession, ctx_data=ctx_data
        )
        endpoint = endpoint.replace("{account_id}", account.account_id)
    if "{vin}" in endpoint:  # pragma: no branch
        vehicle = await renault_vehicle.get_vehicle(
            websession=websession, ctx_data=ctx_data
        )
        endpoint = endpoint.replace("{vin}", vehicle.vin)
    return endpoint


async def http_request(
    websession: aiohttp.ClientSession,
    ctx_data: Dict[str, Any],
    method: str,
    endpoint: str,
    json_body: Optional[Dict[str, Any]] = None,
) -> None:
    """Run HTTP request."""
    endpoint = await http_get_endpoint(websession, ctx_data, endpoint)

    session = await _get_logged_in_session(websession=websession, ctx_data=ctx_data)
    response = await session.http_request(method, endpoint, json_body)

    if ctx_data["json"]:  # pragma: no cover
        click.echo(json.dumps(response.raw_data))
    else:
        click.echo(response.raw_data)
