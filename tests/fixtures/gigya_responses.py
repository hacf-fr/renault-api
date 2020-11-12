"""Mock Gigya responses."""
import datetime

import jwt


MOCK_LOGIN = {"errorCode": 0, "sessionInfo": {"cookieValue": "cookie-value"}}
MOCK_GETACCOUNTINFO = {"errorCode": 0, "data": {"personId": "person-id-1"}}
MOCK_GETJWT = {
    "errorCode": 0,
    "id_token": jwt.encode(
        {"exp": datetime.datetime.now() + datetime.timedelta(days=1)},
        None,  # type: ignore
        "none",
    ).decode("utf-8"),
}
