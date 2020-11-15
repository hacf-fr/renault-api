"""Gigya models."""
from typing import Any, List
from typing import Dict


class KamereonAccountData:
    """Kamereon account data."""

    def __init__(self, raw_data: Dict[str, Any]) -> None:
        """Initialise Kamereon account data."""
        self.raw_data = raw_data

    @property
    def account_id(self) -> str:
        """Return the accountId from the account data."""
        return self.raw_data.get("accountId")

    @property
    def account_type(self) -> str:
        """Return the accountType from the account data."""
        return self.raw_data.get("accountType")

    @property
    def account_status(self) -> str:
        """Return the accountStatus from the account data."""
        return self.raw_data.get("accountStatus")


class KamereonResponse:
    """Base Renault response."""

    def __init__(self, raw_data: Dict[str, Any]) -> None:
        """Initialise Kamereon response."""
        self.raw_data = raw_data


class KamereonPersonResponse(KamereonResponse):
    """Kamereon response to GET on /persons/{gigya_person_id}."""

    @property
    def accounts(self) -> List[KamereonAccountData]:
        """Return the cookieValue from the response sessionInfo."""
        return list(
            KamereonAccountData(raw_value)
            for raw_value in self.raw_data.get("accounts", [])
        )
