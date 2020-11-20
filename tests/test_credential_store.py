"""Test cases for the Gigya client."""
import tempfile
import time
from shutil import copyfile
from unittest import mock

import pytest
from tests import get_jwt

from renault_api.credential_store import CredentialStore
from renault_api.credential_store import FileCredentialStore
from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential


def test_invalid_credential() -> None:
    """Test get/set with simple credential."""
    credential_store = CredentialStore()

    test_key = "test"
    with pytest.raises(TypeError):
        credential_store[test_key] = test_key  # type:ignore

    test_value = Credential("test_value")
    with pytest.raises(TypeError):
        credential_store[test_value] = test_value  # type:ignore


def test_simple_credential() -> None:
    """Test get/set with simple credential."""
    credential_store = CredentialStore()
    test_key = "test"

    # Try to get value from empty store
    assert test_key not in credential_store
    assert not credential_store.get(test_key)
    with pytest.raises(KeyError):
        credential_store[test_key]

    # Set value
    test_value = Credential("test_value")
    credential_store[test_key] = test_value

    # Try to get values from filled store
    assert test_key in credential_store
    assert credential_store.get(test_key) == test_value
    assert credential_store[test_key] == test_value


def test_jwt_credential() -> None:
    """Test get/set with jwt credential."""
    credential_store = CredentialStore()
    test_key = "test"

    # Try to get value from empty store
    assert test_key not in credential_store
    assert not credential_store.get(test_key)
    with pytest.raises(KeyError):
        credential_store[test_key]

    # Set value
    test_value = JWTCredential(get_jwt())
    credential_store[test_key] = test_value

    # Try to get values from filled store
    assert test_key in credential_store
    assert credential_store.get(test_key) == test_value
    assert credential_store[test_key] == test_value

    # Try again with expired
    expired_time = time.time() + 3600
    with mock.patch("time.time", mock.MagicMock(return_value=expired_time)):
        assert test_key not in credential_store
        assert not credential_store.get(test_key)
        with pytest.raises(KeyError):
            credential_store[test_key]


def test_clear() -> None:
    """Test clearance of credential store."""
    credential_store = CredentialStore()
    test_key = "test"
    test_permanent_key = "locale"

    # Try to get value from empty store
    assert test_key not in credential_store
    assert test_permanent_key not in credential_store

    # Set value
    test_value = Credential("test_value")
    test_pemanent_value = Credential("test_locale")
    credential_store[test_key] = test_value
    credential_store[test_permanent_key] = test_pemanent_value

    # Try to get values from filled store
    assert test_key in credential_store
    assert credential_store[test_key] == test_value
    assert test_permanent_key in credential_store
    assert credential_store[test_permanent_key] == test_pemanent_value

    # Try to get values from filled store
    credential_store.clear()

    # Try to get values from filled store
    assert test_key not in credential_store
    assert test_permanent_key in credential_store
    assert credential_store[test_permanent_key] == test_pemanent_value


def test_file_store() -> None:
    """Test clearance of credential store."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Prepare initial store
        old_filename = f"{tmpdirname}/.credentials/renault-api.json"
        old_credential_store = FileCredentialStore(old_filename)
        test_key = "key"
        test_value = Credential("value")
        test_jwt_key = "gigya_jwt"
        test_jwt_value = JWTCredential(get_jwt())
        old_credential_store[test_key] = test_value
        old_credential_store[test_jwt_key] = test_jwt_value

        assert test_key in old_credential_store
        assert old_credential_store.get(test_key) == test_value
        assert old_credential_store[test_key] == test_value
        assert test_jwt_key in old_credential_store
        assert old_credential_store.get(test_jwt_key) == test_jwt_value
        assert old_credential_store[test_jwt_key] == test_jwt_value

        # Copy the data into new file
        new_filename = f"{tmpdirname}/.credentials/renault-api-copy.json"
        copyfile(old_filename, new_filename)
        new_credential_store = FileCredentialStore(new_filename)

        # Check that the data is in the new store
        assert test_key in new_credential_store
        assert new_credential_store.get(test_key) == test_value
        assert new_credential_store[test_key] == test_value
        assert test_jwt_key in new_credential_store
        assert new_credential_store.get(test_jwt_key) == test_jwt_value
        assert new_credential_store[test_jwt_key] == test_jwt_value

        # Try again with expired
        expired_time = time.time() + 3600
        with mock.patch("time.time", mock.MagicMock(return_value=expired_time)):
            assert test_key in new_credential_store
            assert test_jwt_key not in new_credential_store
