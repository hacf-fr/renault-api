"""Test configuration."""
import asyncio
import functools
from typing import AsyncGenerator

import pytest
from aiohttp.client import ClientSession


def pytest_addoption(parser):  # type: ignore
    """Add pytest options."""
    parser.addoption(
        "-E",
        action="store",
        metavar="NAME",
        help="only run tests matching the environment NAME.",
    )


def pytest_configure(config):  # type: ignore
    """Register additional markers."""
    # register an additional marker
    config.addinivalue_line(
        "markers", "env(name): mark test to run only on named environment"
    )


def pytest_runtest_setup(item):  # type: ignore
    """Setup run tests."""
    envnames = [mark.args[0] for mark in item.iter_markers(name="env")]
    if envnames:
        if item.config.getoption("-E") not in envnames:
            pytest.skip("test requires env in {!r}".format(envnames))


@pytest.fixture
async def websession() -> AsyncGenerator[ClientSession, None]:
    """Fixture for generating ClientSession."""
    async with ClientSession() as aiohttp_session:
        yield aiohttp_session

        closed_event = create_aiohttp_closed_event(aiohttp_session)
        await aiohttp_session.close()
        await closed_event.wait()


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
