"""Mock Gigya responses."""
import datetime
import json
from dataclasses import dataclass
from typing import Any

import jwt
from tests.const import TEST_PERSON_ID


@dataclass
class MockGigyaResponse:
    """Mock Gigya response."""

    status: int
    response: Any

    def get_body(self) -> str:
        """Get body as json string."""
        return json.dumps(self.response)


MOCK_LOGIN = MockGigyaResponse(
    status=200,
    response={"errorCode": 0, "sessionInfo": {"cookieValue": "cookie-value"}},
)
MOCK_LOGIN_INVALID_CREDENTIAL = MockGigyaResponse(
    status=200,
    response={
        "errorCode": 403042,
        "errorDetails": "invalid loginID or password",
        "errorMessage": "Invalid LoginID",
    },
)
MOCK_LOGIN_MISSING_SESSION = MockGigyaResponse(
    status=200, response={"errorCode": 0, "sessionInfo": {}}
)
MOCK_GETACCOUNTINFO = MockGigyaResponse(
    status=200, response={"errorCode": 0, "data": {"personId": TEST_PERSON_ID}}
)
MOCK_GETACCOUNTINFO_MISSING_DATA = MockGigyaResponse(
    status=200, response={"errorCode": 0, "data": {}}
)
MOCK_GETJWT = MockGigyaResponse(
    status=200,
    response={
        "errorCode": 0,
        "id_token": jwt.encode(
            {"exp": datetime.datetime.now() + datetime.timedelta(days=1)},
            None,  # type: ignore
            "none",
        ).decode("utf-8"),
    },
)
MOCK_GETJWT_MISSING_TOKEN = MockGigyaResponse(status=200, response={"errorCode": 0})
