"""Command-line interface."""
import logging
from datetime import datetime
from typing import Optional

import click
from aiohttp.client import ClientSession
from click.core import Context

from . import renault_account
from . import renault_client
from . import renault_settings
from . import renault_vehicle
from . import renault_vehicle_ac
from .helpers import coro
from .helpers import create_aiohttp_closed_event
from renault_api.exceptions import RenaultException


def _set_debug(debug: bool, log: bool) -> None:
    """Renault CLI."""
    if debug or log:
        renault_log = logging.getLogger("renault_api")
        renault_log.setLevel(logging.DEBUG)

        if log:
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
    locale: Optional[str],
    account: Optional[str],
    vin: Optional[str],
) -> None:
    """Main entry point for the Renault CLI."""
    ctx.ensure_object(dict)
    if debug or log:
        _set_debug(debug, log)
    if locale:
        ctx.obj["locale"] = locale
    if account:
        ctx.obj["account"] = account
    if vin:
        ctx.obj["vin"] = vin


@main.command()
@click.pass_context
@coro  # type: ignore
async def ac_cancel(ctx: Context) -> None:
    """Cancel air conditionning."""
    async with ClientSession() as websession:
        try:
            await renault_vehicle_ac.cancel(websession=websession, ctx_data=ctx.obj)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession=websession)
            await websession.close()
            await closed_event.wait()


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
@main.command()
@click.pass_context
@coro  # type: ignore
async def ac_history(ctx: Context, start: str, end: str, period: Optional[str]) -> None:
    """Start air conditionning."""
    async with ClientSession() as websession:
        try:
            await renault_vehicle_ac.history(
                websession=websession,
                ctx_data=ctx.obj,
                start=start,
                end=end,
                period=period,
            )
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@click.option(
    "--from", "start", help="Date to start showing history from", required=True
)
@click.option(
    "--to",
    "end",
    help="Date to finish showing history at (cannot be in the future)",
    required=True,
)
@main.command()
@click.pass_context
@coro  # type: ignore
async def ac_sessions(ctx: Context, start: str, end: str) -> None:
    """Start air conditionning."""
    async with ClientSession() as websession:
        try:
            await renault_vehicle_ac.sessions(
                websession=websession,
                ctx_data=ctx.obj,
                start=start,
                end=end,
            )
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@click.option(
    "--temperature", type=int, help="Target temperature (in Celsius)", required=True
)
@click.option(
    "--at",
    default=None,
    help="Date/time at which to complete preconditioning"
    " (defaults to immediate if not given). You can use"
    " times like 'in 5 minutes' or 'tomorrow at 9am'.",
)
@main.command()
@click.pass_context
@coro  # type: ignore
async def ac_start(ctx: Context, temperature: int, at: Optional[str]) -> None:
    """Start air conditionning."""
    async with ClientSession() as websession:
        try:
            await renault_vehicle_ac.start(
                websession=websession,
                ctx_data=ctx.obj,
                temperature=temperature,
                at=at,
            )
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
@click.pass_context
@coro  # type: ignore
async def accounts(ctx: Context) -> None:
    """Display list of accounts."""
    async with ClientSession() as websession:
        try:
            await renault_client.display_accounts(websession, ctx.obj)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
@click.pass_context
@coro  # type: ignore
@click.option("--user", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
async def login(ctx: Context, user: str, password: str) -> None:
    """Login to Renault."""
    async with ClientSession() as websession:
        try:
            await renault_client.login(websession, ctx.obj, user, password)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
def reset() -> None:
    """Clear all credentials/settings from the credential store."""
    renault_settings.reset()


@click.option("--locale", default=None, help="API locale (eg. fr_FR)")
@click.option(
    "--account", default=None, help="Kamereon account ID to use for future calls"
)
@click.option("--vin", default=None, help="Vehicle VIN to use for future calls")
@main.command()
@coro  # type: ignore
async def set(
    locale: Optional[str], account: Optional[str], vin: Optional[str]
) -> None:
    """Store specified settings into credential store."""
    async with ClientSession() as websession:
        try:
            await renault_settings.set_options(websession, locale, account, vin)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
def settings() -> None:
    """Display the current configuration keys."""
    renault_settings.display_settings()


@main.command()
@click.pass_context
@coro  # type: ignore
async def status(ctx: Context) -> None:
    """Display vehicle status."""
    async with ClientSession() as websession:
        try:
            await renault_vehicle.display_status(websession, ctx_data=ctx.obj)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
@click.pass_context
@coro  # type: ignore
async def vehicles(ctx: Context) -> None:
    """Display list of vehicles."""
    async with ClientSession() as websession:
        try:
            await renault_account.display_vehicles(websession, ctx.obj)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


if __name__ == "__main__":
    main(prog_name="renault-api")  # pragma: no cover
