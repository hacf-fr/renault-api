"""Command-line interface."""
from typing import Optional

import click
from aiohttp.client import ClientSession
from click.core import Context

from .core import display_keys
from .core import set_debug
from .core import set_options
from .helpers import coro
from .helpers import create_aiohttp_closed_event
from .kamereon import display_accounts
from .kamereon import do_login
from renault_api.cli.vehicle_status import display_status
from renault_api.cli.vehicles import display_vehicles
from renault_api.exceptions import RenaultException


@click.group()
@click.version_option()
@click.option("--debug", is_flag=True)
@click.option("--log", is_flag=True)
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
    """Renault CLI."""
    ctx.ensure_object(dict)
    if debug or log:
        set_debug(debug, log)
    if locale:
        ctx.obj["locale"] = locale
    if account:
        ctx.obj["account"] = account
    if vin:
        ctx.obj["vin"] = vin


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
    """Set configuration keys."""
    async with ClientSession() as websession:
        try:
            await set_options(websession, locale, account, vin)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
@click.pass_context
@coro  # type: ignore
async def status(ctx: Context) -> None:
    """Set configuration keys."""
    async with ClientSession() as websession:
        try:
            await display_status(
                websession,
                locale=ctx.obj.get("locale"),
                account=ctx.obj.get("account"),
                vin=ctx.obj.get("vin"),
            )
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
@coro  # type: ignore
async def get_keys() -> None:
    """Get the current configuration keys."""
    async with ClientSession() as websession:
        try:
            await display_keys(websession)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
@coro  # type: ignore
@click.option("--user", prompt=True)
@click.option("--password", prompt=True, hide_input=True)
async def login(user: str, password: str) -> None:
    """Login to Renault."""
    async with ClientSession() as websession:
        try:
            await do_login(websession, user, password)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@main.command()
@coro  # type: ignore
async def accounts() -> None:
    """Login to Renault."""
    async with ClientSession() as websession:
        try:
            await display_accounts(websession)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


@click.option(
    "--account",
    default=None,
    help="Kamereon account ID to use",
)
@main.command()
@coro  # type: ignore
async def vehicles(account: Optional[str]) -> None:
    """Login to Renault."""
    async with ClientSession() as websession:
        try:
            await display_vehicles(websession, account)
        except RenaultException as exc:
            raise click.ClickException(str(exc)) from exc
        finally:
            closed_event = create_aiohttp_closed_event(websession)
            await websession.close()
            await closed_event.wait()


if __name__ == "__main__":
    main(prog_name="renault-api")  # pragma: no cover
