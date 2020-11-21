"""Test suite for the renault_api package."""
import datetime
from glob import glob
from typing import List
from typing import Optional

import jwt


def get_jwt(timedelta: Optional[datetime.timedelta] = None) -> str:
    """Read fixture text file as string."""
    if not timedelta:
        timedelta = datetime.timedelta(seconds=900)
    return jwt.encode(
        payload={"exp": datetime.datetime.utcnow() + timedelta},
        key="mock",
        algorithm="HS256",
    ).decode("utf-8")


def get_json_files(parent_dir: str) -> List[str]:
    """Read fixture text file as string."""
    return glob(f"{parent_dir}/*.json")
