"""Test suite for the renault_api package."""
import datetime

import jwt


def get_jwt() -> str:
    """Read fixture text file as string."""
    return jwt.encode(
        payload={"exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=900)},
        key=None,
        algorithm="none",
    ).decode("utf-8")
