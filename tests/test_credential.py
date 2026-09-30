"""Tests for Credential models."""

import time
from unittest import mock

from tests.fixtures import get_jwt

from renault_api.credential import Credential
from renault_api.credential import JWTCredential

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


def test_jwt_clock_skew_margin() -> None:
    """Test a token expiring within the margin is treated as expired."""
    credential = JWTCredential(get_jwt())

    within_margin = time.time() + 900 - 30
    with mock.patch("time.time", mock.MagicMock(return_value=within_margin)):
        assert credential.has_expired()

    beyond_margin = time.time() + 900 - 120
    with mock.patch("time.time", mock.MagicMock(return_value=beyond_margin)):
        assert not credential.has_expired()
