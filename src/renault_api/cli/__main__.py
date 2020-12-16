"""Command-line interface."""
import errno
import logging
import os
from datetime import datetime
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
from . import renault_vehicle_charge
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
    debug: bool,
    log: bool,
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
    if locale:
        ctx.obj["locale"] = locale
    if account:
        ctx.obj["account"] = account
    if vin:  # pragma: no branch
        ctx.obj["vin"] = vin


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


@main.group()
def charge():
    """Charge functionnality."""
    pass


@charge.command(name="history")
@helpers.start_end_option(True)
@click.pass_obj
@helpers.coro_with_websession
async def charge_history(
    ctx_data: Dict[str, Any],
    *,
    start: str,
    end: str,
    period: Optional[str],
    websession: aiohttp.ClientSession,
) -> None:
    """Display charge history."""
    await renault_vehicle_charge.history(
        websession=websession,
        ctx_data=ctx_data,
        start=start,
        end=end,
        period=period,
    )


@charge.command(name="mode")
@click.option(
    "--set",
    help="Target charge mode (schedule_mode/always/always_schedule)",
)
@click.pass_obj
@helpers.coro_with_websession
async def charge_mode(
    ctx_data: Dict[str, Any],
    *,
    set: Optional[str] = None,
    websession: aiohttp.ClientSession,
) -> None:
    """Display or set charge mode."""
    await renault_vehicle_charge.mode(
        websession=websession,
        ctx_data=ctx_data,
        set=set,
    )


@charge.command(name="start")
@click.pass_obj
@helpers.coro_with_websession
async def charge_start(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Start charge."""
    await renault_vehicle_charge.start(
        websession=websession,
        ctx_data=ctx_data,
    )


@charge.command(name="sessions")
@helpers.start_end_option(False)
@click.pass_obj
@helpers.coro_with_websession
async def charge_sessions(
    ctx_data: Dict[str, Any],
    *,
    start: str,
    end: str,
    websession: aiohttp.ClientSession,
) -> None:
    """Display charges."""
    await renault_vehicle_charge.charges(
        websession=websession,
        ctx_data=ctx_data,
        start=start,
        end=end,
    )


@charge.command(name="settings")
@click.option("--id", type=int, help="Schedule ID")
@click.option("--set", is_flag=True, help="Update specified schedule.")
@helpers.days_of_week_option(
    helptext="{} schedule in format `HH:MM,DURATION` or `THH:MMZ,DURATION`"
    "or `clear` to unset."
)
@click.pass_obj
@helpers.coro_with_websession
async def charge_settings(
    ctx_data: Dict[str, Any],
    *,
    set: bool,
    id: Optional[int] = None,
    websession: aiohttp.ClientSession,
    **kwargs: Any,
) -> None:
    """Display or update charging settings."""
    await renault_vehicle_charge.settings(
        websession=websession,
        ctx_data=ctx_data,
        id=id,
        set=set,
        **kwargs,
    )


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


if __name__ == "__main__":  # pragma: no cover
    main(prog_name="renault-api")
