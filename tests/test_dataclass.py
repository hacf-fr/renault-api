"""Test cases for the Renault client API keys."""
import time

from renault_api.dataclass import JWTInfo


def test_jwt_no_expiry() -> None:
    """Test for JWTInfo class."""
    value = "MyValue"
    expiry = None
    jwt_info = JWTInfo(value, expiry)

    assert jwt_info.value == value
    assert jwt_info.expiry is None
    assert not jwt_info.has_expired()


def test_jwt_not_expired() -> None:
    """Test for JWTInfo class."""
    value = "MyValue"
    expiry = time.time() + 60 * 60
    jwt_info = JWTInfo(value, expiry)

    assert jwt_info.value == value
    assert jwt_info.expiry == expiry
    assert not jwt_info.has_expired()


def test_jwt_expired() -> None:
    """Test for JWTInfo class."""
    value = "MyValue"
    expiry = time.time() - 60 * 60
    jwt_info = JWTInfo(value, expiry)

    assert jwt_info.value == value
    assert jwt_info.expiry == expiry
    assert jwt_info.has_expired()
