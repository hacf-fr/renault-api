"""Gigya models."""
from typing import Any
from typing import Dict

from renault_api.exceptions import GigyaResponseException


class GigyaResponse:
    """Base Gigya response."""

    def __init__(self, raw_data: Dict[str, Any]) -> None:
        """Initialise Gigya response."""
        self.raw_data = raw_data

    @property
    def error_code(self) -> int:
        """Return the errorCode from the response."""
        return self.raw_data.get("errorCode", 0)

    def raise_for_error_code(self) -> None:
        """Checks the response information."""
        if self.error_code > 0:
            raise GigyaResponseException(
                self.error_code, self.raw_data.get("errorDetails", "")
            )


class GigyaLoginResponse(GigyaResponse):
    """Gigya response to POST on /accounts.login."""

    @property
    def cookie_value(self) -> int:
        """Return the cookieValue from the response sessionInfo."""
        return self.raw_data.get("sessionInfo", {}).get("cookieValue")


class GigyaGetAccountInfoResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getAccountInfo."""

    @property
    def person_id(self) -> int:
        """Return the personId from the response data."""
        return self.raw_data.get("data", {}).get("personId")


class GigyaGetJWTResponse(GigyaResponse):
    """Gigya response to POST on /accounts.getJWT."""

    @property
    def id_token(self) -> int:
        """Return the id_token from the response data."""
        return self.raw_data.get("id_token")
