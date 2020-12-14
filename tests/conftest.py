"""Test configuration."""
import asyncio
import functools
import pathlib
from typing import Any
from typing import AsyncGenerator
from typing import Generator

import pytest
import pytz
from _pytest.monkeypatch import MonkeyPatch
from aiohttp.client import ClientSession
from aioresponses import aioresponses
from click.testing import CliRunner


@pytest.fixture
async def websession() -> AsyncGenerator[ClientSession, None]:
    """Fixture for generating ClientSession."""
    async with ClientSession() as aiohttp_session:
        yield aiohttp_session

        closed_event = create_aiohttp_closed_event(aiohttp_session)
        await aiohttp_session.close()
        await closed_event.wait()


@pytest.fixture(autouse=True)
def mocked_responses() -> aioresponses:
    """Fixture for mocking aiohttp responses."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def cli_runner(
    monkeypatch: MonkeyPatch, tmpdir: pathlib.Path
) -> Generator[CliRunner, None, None]:
    """Fixture for invoking command-line interfaces."""
    runner = CliRunner()

    monkeypatch.setattr("os.path.expanduser", lambda x: x.replace("~", str(tmpdir)))

    def get_test_zone() -> Any:
        # Get a non UTC zone. Let's use Paris.
        return pytz.timezone("Europe/Paris")

    monkeypatch.setattr("tzlocal.get_localzone", get_test_zone)

    yield runner


def create_aiohttp_closed_event(
    session: ClientSession,
) -> asyncio.Event:  # pragma: no cover
    """Work around aiohttp issue that doesn't properly close transports on exit.

    See https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-639080209

    Args:
        session (ClientSession): session for which to generate the event.

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

    for conn in session.connector._conns.values():  # type: ignore
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
