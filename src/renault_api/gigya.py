"""Gigya client for authentication."""
import logging

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)


class Gigya(object):
    """Gigya client for authentication."""

    def __init__(self, websession: ClientSession) -> None:
        """Initialise Gigya."""
        self._websession = websession

    async def login(self, user: str, password: str) -> None:
        """Send login to Gigya."""
        pass

    async def get_person_id(self) -> str:
        """Get person id."""
        return "person_id"

    async def get_jwt_token(self) -> str:
        """Get JWT token."""
        return "jwt_token"
