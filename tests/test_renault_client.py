"""Tests for RenaultClient."""
from renault_api.renault_client import RenaultClient


def test_renault_client() -> RenaultClient:
    """Ensure RenaultClient can be initialised."""
    client = RenaultClient()
    return client
