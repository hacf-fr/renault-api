"""Helpers for Renault API."""
import asyncio
import functools
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Callable
from typing import Optional
from typing import Tuple
from tzlocal import get_localzone

import aiohttp
import click
import dateparser
import dateutil

from renault_api.exceptions import RenaultException


_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def coro_with_websession(func: Callable[..., Any]) -> Callable[..., Any]:
    """Ensure the routine runs on an event loop with a websession."""

    async def run_command(func: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        async with aiohttp.ClientSession() as websession:
            try:
                kwargs["websession"] = websession
                await func(*args, **kwargs)
            except RenaultException as exc:  # pragma: no cover
                raise click.ClickException(str(exc)) from exc
            finally:
                closed_event = create_aiohttp_closed_event(websession)
                await websession.close()
                await closed_event.wait()

    def wrapper(*args: Any, **kwargs: Any) -> None:
        asyncio.run(run_command(func, *args, **kwargs))

    return functools.update_wrapper(wrapper, func)


def create_aiohttp_closed_event(
    websession: aiohttp.ClientSession,
) -> asyncio.Event:  # pragma: no cover
    """Work around aiohttp issue that doesn't properly close transports on exit.

    See https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-639080209

    Args:
        websession (aiohttp.ClientSession): session for which to generate the event.

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


def parse_dates(start: str, end: str) -> Tuple[datetime, datetime]:
    """Convert start/end string arguments into datetime arguments."""
    parsed_start = dateparser.parse(start)
    parsed_end = dateparser.parse(end)

    if not parsed_start:
        raise ValueError(f"Unable to parse `{start}` into start datetime.")
    if not parsed_end:
        raise ValueError(f"Unable to parse `{end}` into end datetime.")

    return (parsed_start, parsed_end)


def _timezone_offset():
    offset = get_localzone().utcoffset(datetime.now()).total_seconds() / 60
    return offset / 60, offset % 60


def _format_tzdatetime(datetime: str) -> str:
    return (
        dateutil.parser.parse(datetime)
        .astimezone(dateutil.tz.tzlocal())
        .strftime(_DATETIME_FORMAT)
    )


def _format_tztime(time: str) -> str:
    offset_hours, offset_minutes = _timezone_offset()
    raw_hours = int(time[1:3])
    raw_minutes = int(time[4:6])
    return "{:02g}:{:02g}".format(
        (raw_hours + offset_hours) % 24, raw_minutes + offset_minutes
    )


def _format_minutes(mins: float) -> str:
    d = timedelta(minutes=mins)
    return str(d)


def get_display_value(
    value: Optional[Any] = None,
    unit: Optional[str] = None,
    round: Optional[int] = None,
) -> str:
    """Get a display for value."""
    if value is None:
        return ""
    if unit is None:
        return str(value)
    if unit == "tzdatetime":
        return _format_tzdatetime(value)
    if unit == "tztime":
        return _format_tztime(value)
    if unit == "minutes":
        return _format_minutes(value)
    if unit == "kW":
        value = value / 1000
        return f"{value:.2f} {unit}"
    return f"{value} {unit}"
