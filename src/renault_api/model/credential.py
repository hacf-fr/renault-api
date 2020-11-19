"""Credential dataclass."""
import time
from dataclasses import dataclass

import jwt


@dataclass
class Credential:
    """Base credential that never expires."""

    value: str

    def has_expired(self) -> bool:
        """Check if Credential has expired."""
        return False


@dataclass
class JWTCredential(Credential):
    """JWT credential with expiry time."""

    expiry: float

    def __init__(self, value: str) -> None:
        """Initialise JWTCredential."""
        decoded_token = jwt.decode(value, options={"verify_signature": False})

        super().__init__(value=value)
        self.expiry = decoded_token["exp"]

    def has_expired(self) -> bool:
        """Check if JWT token has expired."""
        return self.expiry < time.time()
