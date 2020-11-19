"""Tests for RenaultClient."""
import datetime
import time

import jwt
from unittest import mock

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
    test_expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=900)
    jwt_token = jwt.encode(
        payload={"exp": test_expiry},
        key=None,
        algorithm="none",
    ).decode("utf-8")

    credential = JWTCredential(jwt_token)

    assert credential.value == jwt_token
    assert not credential.has_expired()

    expired_time = time.time() + 3600
    with mock.patch("time.time", mock.MagicMock(return_value=expired_time)):
        assert credential.has_expired()
