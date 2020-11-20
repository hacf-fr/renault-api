"""Kamereon client for interaction with Renault servers."""
import json
import os
from typing import Dict
from typing import Optional

from renault_api.model.credential import Credential
from renault_api.model.credential import JWTCredential


PERMANENT_KEYS = ["locale"]


class CredentialStore:
    """Credential store."""

    def __init__(self) -> None:
        """Initialise the credential store."""
        self._store: Dict[str, Credential] = {}

    def __getitem__(self, name: str) -> Credential:
        """Get a credential the credential store."""
        if name in list(self._store.keys()):
            cred = self._store[name]
            if not cred.has_expired():
                return cred
        raise KeyError(name)

    def get(self, name: str) -> Optional[Credential]:
        """Get a credential the credential store."""
        if name in list(self._store.keys()):
            cred = self._store[name]
            if not cred.has_expired():
                return cred
        return None

    def __setitem__(self, name: str, value: Credential) -> None:
        """Add a credential to the credential store."""
        if not isinstance(name, str):  # pragma: no cover
            raise TypeError("`name` must be a string")
        if not isinstance(value, Credential):  # pragma: no cover
            raise TypeError("`value` must be a Credential")

        self._store[name] = value
        self._write()

    def __contains__(self, name: str) -> bool:
        """Check if a credential is in the credential store."""
        if name in self._store:
            cred = self._store[name]
            if not cred.has_expired():
                return True
        return False

    def _write(self) -> None:
        """Writes the content to fixed storage."""
        pass

    def clear(self) -> None:
        """Remove all non-permanent keys."""
        for key in list(self._store.keys()):
            if key not in PERMANENT_KEYS:
                del self._store[key]
        self._write()


class CredentialEncoder(json.JSONEncoder):
    """Custom encoder for Credential class."""

    def default(self, obj: Credential) -> str:
        """Store the value."""
        return obj.value


class FileCredentialStore(CredentialStore):
    """Credential store with items stored in a file."""

    def __init__(self, store_location: str) -> None:
        """Initialise the credential store."""
        super().__init__()
        self._store_location = store_location
        self._read()

    def _read(self) -> None:
        """Read data from store location."""
        if not os.path.exists(self._store_location):
            return
        with open(self._store_location) as json_file:
            data = json.load(json_file)
            for key, value in data.items():
                if key == "gigya_jwt":
                    self[key] = JWTCredential(value)
                else:
                    self[key] = Credential(value)

    def _write(self) -> None:
        """Write data to store location."""
        dirname = os.path.dirname(self._store_location)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        with open(self._store_location, "w") as json_file:
            json.dump(self._store, json_file, cls=CredentialEncoder)
