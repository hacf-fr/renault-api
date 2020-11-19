"""Tests for RenaultClient."""
import time
from unittest import mock

from tests import get_jwt

from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential

TEST_VALUE = "test-value"


def test_simple_credential() -> None:
    """Test for Credential class."""
    credential = Credential(TEST_VALUE)

    assert credential.value == TEST_VALUE
    assert not credential.has_expired()


def test_jwt() -> None:
    """Test for Credential class."""
    jwt_token = get_jwt()

    credential = JWTCredential(jwt_token)

    assert credential.value == jwt_token
    assert not credential.has_expired()

    expired_time = time.time() + 3600
    with mock.patch("time.time", mock.MagicMock(return_value=expired_time)):
        assert credential.has_expired()
