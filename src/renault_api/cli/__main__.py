"""Command-line interface."""
import errno
import json
import logging
import os
from datetime import datetime
from io import TextIOWrapper
from typing import Any
from typing import Dict
from typing import Optional

import aiohttp
import click
from click.core import Context

from . import helpers
from . import renault_account
from . import renault_client
from . import renault_settings
from . import renault_vehicle
from .charge import commands as charge_commands
from .hvac import commands as hvac_commands
from renault_api.credential_store import FileCredentialStore


_WARNING_DEBUG_ENABLED = (
    "Debug output enabled. Logs may contain personally identifiable "
    "information and account credentials! Be sure to sanitise these logs "
    "before sending them to a third party or posting them online."
)


def _check_for_debug(debug: bool, log: bool) -> None:
    """Renault CLI."""
    if debug or log:
        renault_log = logging.getLogger("renault_api")
        renault_log.setLevel(logging.DEBUG)

        if log:
            # create directory
            try:
                os.makedirs("logs")
            except OSError as e:  # pragma: no cover
                if e.errno != errno.EEXIST:
                    raise

            # create formatter and add it to the handlers
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            # create file handler which logs even debug messages
            fh = logging.FileHandler(f"logs/{datetime.today():%Y-%m-%d}.log")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(formatter)

            # And enable our own debug logging
            renault_log.addHandler(fh)

        if debug:
            logging.basicConfig()

        renault_log.warning(_WARNING_DEBUG_ENABLED)


@click.group()
@click.version_option()
@click.option("--debug", is_flag=True, help="Display debug traces.")
@click.option("--log", is_flag=True, help="Log debug traces to file.")
@click.option("--json", is_flag=True, help="Return data as JSON")
@click.option("--locale", default=None, help="API locale (eg. fr_FR)")
@click.option(
    "--account",
    default=None,
    help="Kamereon account ID to use",
)
@click.option("--vin", default=None, help="Vehicle VIN to use")
@click.pass_context
def main(
    ctx: Context,
    *,
    debug: bool,
    log: bool,
    json: bool,
    locale: Optional[str] = None,
    account: Optional[str] = None,
    vin: Optional[str] = None,
) -> None:
    """Main entry point for the Renault CLI."""
    ctx.ensure_object(dict)
    ctx.obj["credential_store"] = FileCredentialStore(
        os.path.expanduser(renault_settings.CREDENTIAL_PATH)
    )
    _check_for_debug(debug, log)
    ctx.obj["json"] = json
    if locale:
        ctx.obj["locale"] = locale
    if account:
        ctx.obj["account"] = account
    if vin:  # pragma: no branch
        ctx.obj["vin"] = vin


main.add_command(charge_commands.charge)
main.add_command(hvac_commands.hvac)


@main.command()
@click.pass_obj
@helpers.coro_with_websession
async def accounts(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Display list of accounts."""
    await renault_client.display_accounts(websession, ctx_data)


@main.command()
@click.option("--user", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
@click.pass_obj
@helpers.coro_with_websession
async def login(
    ctx_data: Dict[str, Any],
    *,
    user: str,
    password: str,
    websession: aiohttp.ClientSession,
) -> None:
    """Login to Renault."""
    await renault_client.login(websession, ctx_data, user, password)


@main.command()
def reset() -> None:
    """Clear all credentials/settings from the credential store."""
    renault_settings.reset()


@main.command()
@click.option("--locale", default=None, help="API locale (eg. fr_FR)")
@click.option(
    "--account", default=None, help="Kamereon account ID to use for future calls"
)
@click.option("--vin", default=None, help="Vehicle VIN to use for future calls")
@click.pass_obj
@helpers.coro_with_websession
async def set(
    ctx_data: Dict[str, Any],
    *,
    locale: Optional[str] = None,
    account: Optional[str] = None,
    vin: Optional[str] = None,
    websession: aiohttp.ClientSession,
) -> None:
    """Store specified settings into credential store."""
    await renault_settings.set_options(websession, ctx_data, locale, account, vin)


@main.command()
@click.pass_obj
def settings(ctx_data: Dict[str, Any]) -> None:
    """Display the current configuration keys."""
    renault_settings.display_settings(ctx_data)


@main.command()
@click.pass_obj
@helpers.coro_with_websession
async def status(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Display vehicle status."""
    await renault_vehicle.display_status(websession, ctx_data)


@main.command()
@click.pass_obj
@helpers.coro_with_websession
async def vehicles(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Display list of vehicles."""
    await renault_account.display_vehicles(websession, ctx_data)


@main.command()
@click.pass_obj
@helpers.coro_with_websession
async def vehicle(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Display vehicle details."""
    await renault_vehicle.display_vehicle(websession, ctx_data)


@main.command()
@click.pass_obj
@helpers.coro_with_websession
async def contracts(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Display vehicle contracts."""
    await renault_vehicle.display_contracts(websession, ctx_data)


@main.group()
def http() -> None:
    """Raw HTTP."""
    pass


@http.command(name="get")
@click.argument("endpoint")
@click.pass_obj
@helpers.coro_with_websession
async def http_get(
    ctx_data: Dict[str, Any],
    *,
    endpoint: str,
    websession: aiohttp.ClientSession,
) -> None:
    """Process HTTP GET request on endpoint."""
    await renault_client.http_request(websession, ctx_data, "GET", endpoint)


@http.command(name="post-file")
@click.argument("endpoint")
@click.argument("json-body", type=click.File("rb"))
@click.pass_obj
@helpers.coro_with_websession
async def http_post_file(
    ctx_data: Dict[str, Any],
    *,
    endpoint: str,
    json_body: TextIOWrapper,
    websession: aiohttp.ClientSession,
) -> None:
    """Process HTTP POST request on endpoint."""
    await renault_client.http_request(
        websession, ctx_data, "POST", endpoint, json.load(json_body)
    )


@http.command(name="post")
@click.argument("endpoint")
@click.argument("json-body")
@click.pass_obj
@helpers.coro_with_websession
async def http_post(
    ctx_data: Dict[str, Any],
    *,
    endpoint: str,
    json_body: str,
    websession: aiohttp.ClientSession,
) -> None:
    """Process HTTP POST request on endpoint."""
    await renault_client.http_request(
        websession, ctx_data, "POST", endpoint, json.loads(json_body)
    )


if __name__ == "__main__":  # pragma: no cover
    main(prog_name="renault-api")
