"""Command-line interface."""
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


def _set_debug(debug: bool, log: bool) -> None:  # pragma: no cover
    """Renault CLI."""
    if debug or log:
        renault_log = logging.getLogger("renault_api")
        renault_log.setLevel(logging.DEBUG)

        if log:  # pragma: no cover
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

        renault_log.warning(
            "Debug output enabled. Logs may contain personally identifiable "
            "information and account credentials! Be sure to sanitise these logs "
            "before sending them to a third party or posting them online."
        )


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
    if debug or log:
        _set_debug(debug, log)
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


@main.command()
@click.option(
    "--from", "start", help="Date to start showing history from", required=True
)
@click.option(
    "--to",
    "end",
    help="Date to finish showing history at (cannot be in the future)",
    required=True,
)
@click.option(
    "--period",
    default="month",
    help="Period over which to aggregate.",
    type=click.Choice(["day", "month"], case_sensitive=False),
)
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
    """Display air conditioning history."""
    await renault_vehicle_charge.history(
        websession=websession,
        ctx_data=ctx_data,
        start=start,
        end=end,
        period=period,
    )


@main.command()
@click.option(
    "--mode",
    help="Target charge mode (schedule_mode/alway/always_schedule)",
)
@click.pass_obj
@helpers.coro_with_websession
async def charge_mode(
    ctx_data: Dict[str, Any],
    *,
    mode: Optional[str] = None,
    websession: aiohttp.ClientSession,
) -> None:
    """Display or set charge mode."""
    await renault_vehicle_charge.mode(
        websession=websession,
        ctx_data=ctx_data,
        mode=mode,
    )


@main.command()
@click.pass_obj
@helpers.coro_with_websession
async def charging_start(
    ctx_data: Dict[str, Any],
    *,
    websession: aiohttp.ClientSession,
) -> None:
    """Start charge."""
    await renault_vehicle_charge.start(
        websession=websession,
        ctx_data=ctx_data,
    )


@main.command()
@click.option(
    "--from", "start", help="Date to start showing history from", required=True
)
@click.option(
    "--to",
    "end",
    help="Date to finish showing history at (cannot be in the future)",
    required=True,
)
@click.pass_obj
@helpers.coro_with_websession
async def charges(
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


@main.command()
@click.option("--id", type=int, help="Schedule ID")
@click.pass_obj
@helpers.coro_with_websession
async def charging_settings(
    ctx_data: Dict[str, Any],
    *,
    id: Optional[int] = None,
    websession: aiohttp.ClientSession,
) -> None:
    """Display charging settings."""
    await renault_vehicle_charge.settings(
        websession=websession,
        ctx_data=ctx_data,
        id=id,
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
