"""Override classes for PyZE."""
from typing import Optional

from pyze.api.credentials import BasicCredentialStore  # type: ignore
from pyze.api.credentials import PERMANENT_KEYS
from pyze.api.gigya import Gigya  # type: ignore
from pyze.api.kamereon import Kamereon  # type: ignore

from .const import CONF_GIGYA_URL
from .const import CONF_KAMEREON_APIKEY
from .const import CONF_KAMEREON_URL
from .const import CONF_LOCALE

# For some reason, PyZE only puts the API keys as permanent keys!
# We want all these to stay permanent.
PERMANENT_KEYS.extend([CONF_GIGYA_URL, CONF_KAMEREON_URL, CONF_LOCALE])


# For some reason, PyZE writes the account id into the credential store!
# This makes it very difficult to have parallel Kamereon objects.
class KamereonOverride(Kamereon):  # type: ignore
    """Override Kamereon object."""

    def __init__(
        self,
        credentials: BasicCredentialStore,
        gigya: Gigya,
        country: Optional[str],
    ) -> None:
        """Initialise Kamereon override."""
        super().__init__(
            api_key=credentials[CONF_KAMEREON_APIKEY],
            credentials=credentials,
            gigya=gigya,
            country=country,
            root_url=credentials[CONF_KAMEREON_URL],
        )
        self._account_id: Optional[str] = None

    def set_account_id(self, account_id: str) -> None:
        """Set account id."""
        self._account_id = account_id

    def get_account_id(self) -> Optional[str]:
        """Get account id."""
        return self._account_id
