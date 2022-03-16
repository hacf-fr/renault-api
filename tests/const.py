"""Constants for the test suite."""
from renault_api.const import AVAILABLE_LOCALES
from renault_api.const import CONF_GIGYA_APIKEY
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_APIKEY
from renault_api.const import CONF_KAMEREON_URL


REDACTED = "*PRIVATE*"
TO_REDACT = ["accountId", "id", "radioCode", "registrationNumber", "vin"]

TEST_ACCOUNT_ID = "account-id-1"
TEST_LOCALE = "fr_FR"
TEST_LOGIN_TOKEN = "sample-cookie-value"  # noqa: S105
TEST_PASSWORD = "test_password"  # noqa: S105
TEST_PERSON_ID = "person-id-1"
TEST_USERNAME = "test@example.com"
TEST_VIN = "VF1AAAAA555777999"

TEST_COUNTRY = TEST_LOCALE[-2:]
TEST_LOCALE_DETAILS = AVAILABLE_LOCALES[TEST_LOCALE]
TEST_GIGYA_APIKEY = TEST_LOCALE_DETAILS[CONF_GIGYA_APIKEY]
TEST_GIGYA_URL = TEST_LOCALE_DETAILS[CONF_GIGYA_URL]
TEST_KAMEREON_APIKEY = TEST_LOCALE_DETAILS[CONF_KAMEREON_APIKEY]
TEST_KAMEREON_URL = TEST_LOCALE_DETAILS[CONF_KAMEREON_URL]

TEST_SCHEDULES = {
    "schedules": [
        {
            "id": 1,
            "activated": True,
            "monday": {"startTime": "T12:00Z", "duration": 15},
            "tuesday": {"startTime": "T04:30Z", "duration": 420},
            "wednesday": {"startTime": "T22:30Z", "duration": 420},
            "thursday": {"startTime": "T22:00Z", "duration": 420},
            "friday": {"startTime": "T12:15Z", "duration": 15},
            "saturday": {"startTime": "T12:30Z", "duration": 30},
            "sunday": {"startTime": "T12:45Z", "duration": 45},
        }
    ]
}
