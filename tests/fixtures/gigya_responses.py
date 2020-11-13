"""Mock Gigya responses."""
import datetime

import jwt


MOCK_LOGIN = {"errorCode": 0, "sessionInfo": {"cookieValue": "cookie-value"}}
MOCK_LOGIN_INVALID_CREDENTIAL = {
    "errorCode": 403042,
    "errorDetails": "invalid loginID or password",
    "errorMessage": "Invalid LoginID",
}
MOCK_LOGIN_MISSING_SESSION = {"errorCode": 0, "sessionInfo": {}}
MOCK_GETACCOUNTINFO = {"errorCode": 0, "data": {"personId": "person-id-1"}}
MOCK_GETACCOUNTINFO_MISSING_DATA = {"errorCode": 0, "data": {}}
MOCK_GETJWT = {
    "errorCode": 0,
    "id_token": jwt.encode(
        {"exp": datetime.datetime.now() + datetime.timedelta(days=1)},
        None,  # type: ignore
        "none",
    ).decode("utf-8"),
}
MOCK_GETJWT_MISSING_TOKEN = {"errorCode": 0}
