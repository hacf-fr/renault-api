"""Tests for Kamereon API."""
import aiohttp
import pytest
from aioresponses import aioresponses
from aioresponses.core import RequestCall
from tests import fixtures
from tests.const import TEST_ACCOUNT_ID
from tests.const import TEST_COUNTRY
from tests.const import TEST_KAMEREON_APIKEY
from tests.const import TEST_KAMEREON_URL
from tests.const import TEST_PERSON_ID
from tests.const import TEST_VIN
from yarl import URL

from renault_api import kamereon
from renault_api.kamereon import exceptions


@pytest.mark.asyncio
async def test_get_person(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test get_person."""
    fixtures.inject_get_person(mocked_responses)

    person = await kamereon.get_person(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=fixtures.get_jwt(),
        country=TEST_COUNTRY,
        person_id=TEST_PERSON_ID,
    )
    assert person.accounts is not None
    assert len(person.accounts) == 2


@pytest.mark.asyncio
async def test_get_account_vehicles(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test get_account_vehicles."""
    fixtures.inject_get_vehicles(mocked_responses, "zoe_40.1.json")

    await kamereon.get_account_vehicles(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=fixtures.get_jwt(),
        country=TEST_COUNTRY,
        account_id=TEST_ACCOUNT_ID,
    )


@pytest.mark.asyncio
async def test_get_vehicle_data(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test get_vehicle_data."""
    fixtures.inject_get_battery_status(mocked_responses)

    assert await kamereon.get_vehicle_data(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=fixtures.get_jwt(),
        country=TEST_COUNTRY,
        account_id=TEST_ACCOUNT_ID,
        vin=TEST_VIN,
        endpoint="battery-status",
    )


@pytest.mark.asyncio
async def test_get_vehicle_data_xml_bad_gateway(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test get_vehicle_data with invalid xml data."""
    fixtures.inject_get_battery_status(mocked_responses, "error/bad_gateway.html")

    with pytest.raises(exceptions.KamereonResponseException) as excinfo:
        await kamereon.get_vehicle_data(
            websession=websession,
            root_url=TEST_KAMEREON_URL,
            api_key=TEST_KAMEREON_APIKEY,
            gigya_jwt=fixtures.get_jwt(),
            country=TEST_COUNTRY,
            account_id=TEST_ACCOUNT_ID,
            vin=TEST_VIN,
            endpoint="battery-status",
        )
    assert excinfo.value.error_code == "Invalid JSON"
    assert excinfo.value.error_details.startswith(
        "<html>\n  <head>\n    <title>502 Bad Gateway</title>"
    )


@pytest.mark.asyncio
async def test_set_vehicle_action(
    websession: aiohttp.ClientSession, mocked_responses: aioresponses
) -> None:
    """Test set_vehicle_action."""
    url = fixtures.inject_set_hvac_start(mocked_responses, "cancel")
    assert await kamereon.set_vehicle_action(
        websession=websession,
        root_url=TEST_KAMEREON_URL,
        api_key=TEST_KAMEREON_APIKEY,
        gigya_jwt=fixtures.get_jwt(),
        country=TEST_COUNTRY,
        account_id=TEST_ACCOUNT_ID,
        vin=TEST_VIN,
        endpoint="hvac-start",
        attributes={"action": "cancel"},
    )

    expected_json = {"data": {"type": "HvacStart", "attributes": {"action": "cancel"}}}

    request: RequestCall = mocked_responses.requests[("POST", URL(url))][0]
    assert expected_json == request.kwargs["json"]
