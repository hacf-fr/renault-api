"""Constants for the test suite fixtures."""
from renault_api.const import AVAILABLE_LOCALES
from renault_api.const import CONF_GIGYA_URL
from renault_api.const import CONF_KAMEREON_URL


TEST_ACCOUNT_ID = "accound-id-1"
TEST_LOCALE = "fr_FR"
TEST_PASSWORD = "test_password"
TEST_PERSON_ID = "person-id-1"
TEST_USERNAME = "test@example.com"
TEST_VIN = "VF1AAAAA555777999"

TEST_COUNTRY = TEST_LOCALE[-2:]
TEST_LOCALE_DETAILS = AVAILABLE_LOCALES[TEST_LOCALE]
TEST_GIGYA_URL = TEST_LOCALE_DETAILS[CONF_GIGYA_URL]
TEST_KAMEREON_URL = TEST_LOCALE_DETAILS[CONF_KAMEREON_URL]
