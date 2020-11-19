"""Test suite for the renault_api package."""
import datetime
from glob import glob
from typing import List

import jwt


def get_jwt() -> str:
    """Read fixture text file as string."""
    return jwt.encode(
        payload={"exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=900)},
        key="mock",
        algorithm="HS256",
    ).decode("utf-8")


def get_json_files(parent_dir: str) -> List[str]:
    """Read fixture text file as string."""
    return glob(f"{parent_dir}/*.json")
