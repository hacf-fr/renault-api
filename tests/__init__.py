"""Test suite for the renault_api package."""
import datetime
from glob import glob
from typing import Any
from typing import List
from typing import Optional
from typing import Type

import jwt
from marshmallow.schema import Schema


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


def get_file_content(filename: str) -> str:
    """Read fixture text file as string."""
    with open(filename, "r") as file:
        content = file.read()
    if filename.endswith("get_jwt.json"):
        content = content.replace("sample-jwt-token", get_jwt())
    return content


def get_response_content(path: str, schema: Type[Schema]) -> Any:
    """Read fixture text file as string."""
    with open(path, "r") as file:
        content = file.read()
    return schema.loads(content)
