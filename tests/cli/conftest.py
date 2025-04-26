"""Test configuration."""

from collections.abc import Generator
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mocked_locale() -> Generator[None, None, None]:
    """Fixture for mocking aiohttp responses."""
    with patch(
        "renault_api.cli.renault_client.getlocale", return_value=("fr_CA", None)
    ):
        yield
