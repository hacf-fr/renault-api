"""Helpers for Renault API."""
import asyncio
import functools
from typing import Any
from typing import Callable
from typing import cast
from typing import TypeVar

import click
from aiohttp import ClientSession

from renault_api.exceptions import RenaultException

F = TypeVar("F", bound=Callable[..., Any])


def coro_with_websession(func: F) -> F:
    """Ensure the routine runs on an event loop CLI."""

    async def run_command(func: F, *args: Any, **kwargs: Any) -> None:
        async with ClientSession() as websession:
            try:
                kwargs["websession"] = websession
                await func(*args, **kwargs)
            except RenaultException as exc:
                raise click.ClickException(str(exc)) from exc
            finally:
                closed_event = create_aiohttp_closed_event(websession)
                await websession.close()
                await closed_event.wait()

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(run_command(func, *args, **kwargs))

    return cast(F, wrapper)


def create_aiohttp_closed_event(
    websession: ClientSession,
) -> asyncio.Event:  # pragma: no cover
    """Work around aiohttp issue that doesn't properly close transports on exit.

    See https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-639080209

    Args:
        websession (ClientSession): session for which to generate the event.

    Returns:
        An event that will be set once all transports have been properly closed.
    """
    transports = 0
    all_is_lost = asyncio.Event()

    def connection_lost(exc, orig_lost):  # type: ignore
        nonlocal transports

        try:
            orig_lost(exc)
        finally:
            transports -= 1
            if transports == 0:
                all_is_lost.set()

    def eof_received(orig_eof_received):  # type: ignore
        try:
            orig_eof_received()
        except AttributeError:
            # It may happen that eof_received() is called after
            # _app_protocol and _transport are set to None.
            pass

    for conn in websession.connector._conns.values():  # type: ignore
        for handler, _ in conn:
            proto = getattr(handler.transport, "_ssl_protocol", None)
            if proto is None:
                continue

            transports += 1
            orig_lost = proto.connection_lost
            orig_eof_received = proto.eof_received

            proto.connection_lost = functools.partial(
                connection_lost, orig_lost=orig_lost
            )
            proto.eof_received = functools.partial(
                eof_received, orig_eof_received=orig_eof_received
            )

    if transports == 0:
        all_is_lost.set()

    return all_is_lost
