"""Helpers for the test suite of the renault_api package."""
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

from tests import get_jwt
from tests.const import TEST_PERSON_ID

from renault_api.session_provider import BaseSessionProvider


def get_session_provider() -> BaseSessionProvider:
    """Fixture for testing BaseSessionProvider."""
    session_provider = BaseSessionProvider()
    session_provider.login = MagicMock(return_value=None)
    session_provider.get_person_id = AsyncMock(return_value=TEST_PERSON_ID)
    session_provider.get_jwt_token = AsyncMock(return_value=get_jwt())
    return session_provider
