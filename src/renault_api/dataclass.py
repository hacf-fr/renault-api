"""Data classes for Renault API."""
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class JWTInfo:
    """JWT with associated expiry time."""

    value: str
    expiry: Optional[float]

    def has_expired(self) -> bool:
        """Check if JWT has expired."""
        if not self.expiry:
            return False
        return self.expiry < time.time()
