"""Test configuration."""

import asyncio
import functools
import pathlib
from collections.abc import AsyncGenerator
from collections.abc import Generator
from datetime import datetime
from datetime import timedelta
from datetime import tzinfo
from typing import Any

import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from click.testing import CliRunner


@pytest_asyncio.fixture
async def websession() -> AsyncGenerator[ClientSession, None]:
    """Fixture for generating ClientSession."""
    async with ClientSession() as aiohttp_session:
        yield aiohttp_session

        closed_event = create_aiohttp_closed_event(aiohttp_session)
        await aiohttp_session.close()
        await closed_event.wait()


@pytest.fixture(autouse=True)
def mocked_responses() -> Generator[aioresponses, None, None]:
    """Fixture for mocking aiohttp responses."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def cli_runner(monkeypatch: MonkeyPatch, tmpdir: pathlib.Path) -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    runner = CliRunner()

    monkeypatch.setattr("os.path.expanduser", lambda x: x.replace("~", str(tmpdir)))

    class TZ1(tzinfo):
        def utcoffset(self, dt: datetime | None) -> timedelta:
            return timedelta(hours=1)

        def dst(self, dt: datetime | None) -> timedelta:
            return timedelta(0)

        def tzname(self, dt: datetime | None) -> str:
            return "+01:00"

        def __repr__(self) -> str:
            return f"{self.__class__.__name__}()"

    def get_test_zone() -> Any:
        # Get a non UTC zone, avoiding DST on standard zones.
        return TZ1()

    monkeypatch.setattr("tzlocal.get_localzone", get_test_zone)

    return runner


def create_aiohttp_closed_event(
    session: ClientSession,
) -> asyncio.Event:
    """Work around aiohttp issue that doesn't properly close transports on exit.

    See https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-639080209

    Args:
        session (ClientSession): session for which to generate the event.

    Returns:
        An event that will be set once all transports have been properly closed.
    """
    transports = 0
    all_is_lost = asyncio.Event()

    def connection_lost(exc, orig_lost):  # type: ignore[no-untyped-def]
        nonlocal transports

        try:
            orig_lost(exc)
        finally:
            transports -= 1
            if transports == 0:
                all_is_lost.set()

    def eof_received(orig_eof_received):  # type: ignore[no-untyped-def]
        try:
            orig_eof_received()
        except AttributeError:
            # It may happen that eof_received() is called after
            # _app_protocol and _transport are set to None.
            pass

    for conn in session.connector._conns.values():  # type: ignore[union-attr]
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
