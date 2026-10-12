"""Gigya API."""

import logging
from json import JSONDecodeError
from typing import Any
from typing import cast

import aiohttp
from marshmallow.schema import Schema

from . import models
from . import schemas
from .exceptions import GigyaException

GIGYA_JWT = "gigya_jwt"
GIGYA_LOGIN_TOKEN = "gigya_login_token"  # nosec
GIGYA_PERSON_ID = "gigya_person_id"
GIGYA_KEYS = [GIGYA_JWT, GIGYA_LOGIN_TOKEN, GIGYA_PERSON_ID]

# Device identifiers, set as cookies by accounts.webSdkBootstrap. They identify
# the device that Gigya remembers after two-factor authentication.
GIGYA_GMID = "gigya_gmid"
GIGYA_UCID = "gigya_ucid"
GIGYA_DEVICE_ID_KEYS = {GIGYA_GMID: "gmid", GIGYA_UCID: "ucid"}

_LOGGER = logging.getLogger(__name__)


async def request(
    websession: aiohttp.ClientSession,
    method: str,
    url: str,
    *,
    schema: Schema,
    data: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    cookies: dict[str, str] | None = None,
) -> models.GigyaResponse:
    """Send request to Gigya."""
    async with websession.request(
        method, url, data=data, params=params, cookies=cookies
    ) as http_response:
        response_text = await http_response.text()
        # Don't log on Gigya, to avoid unnecessary exposure.
        try:
            gigya_response: models.GigyaResponse = schema.loads(response_text)
        except JSONDecodeError as err:
            raise GigyaException("Gigya responded with invalid JSON") from err
        # Check for Gigya error
        gigya_response.raise_for_error_code()
        # Check for HTTP error
        http_response.raise_for_status()

        return gigya_response


async def login(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    *,
    login_id: str,
    password: str,
    device_ids: dict[str, str] | None = None,
) -> models.GigyaLoginResponse:
    """Send POST to /accounts.login.

    `device_ids` (see `get_device_ids`) identify a device remembered after
    two-factor authentication.
    """
    return cast(
        models.GigyaLoginResponse,
        await request(
            websession,
            "POST",
            f"{root_url}/accounts.login",
            data={
                "ApiKey": api_key,
                "loginID": login_id,
                "password": password,
            },
            schema=schemas.GigyaLoginResponseSchema,
            cookies=device_ids,
        ),
    )


async def get_account_info(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_token: str,
) -> models.GigyaGetAccountInfoResponse:
    """Send POST to /accounts.getAccountInfo."""
    return cast(
        models.GigyaGetAccountInfoResponse,
        await request(
            websession,
            "POST",
            f"{root_url}/accounts.getAccountInfo",
            data={
                "ApiKey": api_key,
                "login_token": login_token,
            },
            schema=schemas.GigyaGetAccountInfoResponseSchema,
        ),
    )


async def get_jwt(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    login_token: str,
) -> models.GigyaGetJWTResponse:
    """Send POST to /accounts.getJWT."""
    return cast(
        models.GigyaGetJWTResponse,
        await request(
            websession,
            "POST",
            f"{root_url}/accounts.getJWT",
            data={
                "ApiKey": api_key,
                "login_token": login_token,
                # gigyaDataCenter may be needed for future jwt validation
                "fields": "data.personId,data.gigyaDataCenter",
                "expiration": 900,
            },
            schema=schemas.GigyaGetJWTResponseSchema,
        ),
    )


async def get_device_ids(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
) -> dict[str, str]:
    """Send GET to /accounts.webSdkBootstrap and return the device identifiers.

    They are returned as the `gmid`/`ucid` cookies of the response, and must
    be passed (as `device_ids`) to the two-factor-authentication calls below,
    and to `login` once the challenge is completed. They are read from the
    response rather than from the session cookie jar, which may be shared.
    """
    async with websession.request(
        "GET",
        f"{root_url}/accounts.webSdkBootstrap",
        params={"APIKey": api_key},
    ) as http_response:
        http_response.raise_for_status()
        cookies = http_response.cookies

    return {
        name: cookies[name].value
        for name in GIGYA_DEVICE_ID_KEYS.values()
        if name in cookies
    }


async def init_tfa(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    *,
    device_ids: dict[str, str],
    reg_token: str,
) -> models.GigyaTfaInitResponse:
    """Send GET to /accounts.tfa.initTFA to start an email one-time-code challenge.

    `reg_token` comes from `PendingTwoFactorAuthenticationException.reg_token`,
    raised by `login` when the account requires two-factor authentication.
    """
    return cast(
        models.GigyaTfaInitResponse,
        await request(
            websession,
            "GET",
            f"{root_url}/accounts.tfa.initTFA",
            params={
                "APIKey": api_key,
                "regToken": reg_token,
                "provider": "gigyaEmail",
                "mode": "verify",
                **device_ids,
            },
            schema=schemas.GigyaTfaInitResponseSchema,
            cookies=device_ids,
        ),
    )


async def get_tfa_emails(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    *,
    device_ids: dict[str, str],
    gigya_assertion: str,
) -> models.GigyaTfaEmailListResponse:
    """Send GET to /accounts.tfa.email.getEmails to list the emails eligible for TFA."""
    return cast(
        models.GigyaTfaEmailListResponse,
        await request(
            websession,
            "GET",
            f"{root_url}/accounts.tfa.email.getEmails",
            params={"APIKey": api_key, "gigyaAssertion": gigya_assertion},
            schema=schemas.GigyaTfaEmailListResponseSchema,
            cookies=device_ids,
        ),
    )


async def send_tfa_email_code(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    *,
    device_ids: dict[str, str],
    gigya_assertion: str,
    email_id: str,
    lang: str | None = None,
) -> models.GigyaTfaSendEmailCodeResponse:
    """Send GET to /accounts.tfa.email.sendVerificationCode to email the OTP code."""
    return cast(
        models.GigyaTfaSendEmailCodeResponse,
        await request(
            websession,
            "GET",
            f"{root_url}/accounts.tfa.email.sendVerificationCode",
            params={
                "APIKey": api_key,
                "gigyaAssertion": gigya_assertion,
                "emailID": email_id,
                **({"lang": lang} if lang else {}),
            },
            schema=schemas.GigyaTfaSendEmailCodeResponseSchema,
            cookies=device_ids,
        ),
    )


async def complete_tfa_email_verification(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    *,
    device_ids: dict[str, str],
    gigya_assertion: str,
    phv_token: str,
    code: str,
) -> models.GigyaTfaEmailCompleteVerificationResponse:
    """Send GET to /accounts.tfa.email.completeVerification with the emailed code."""
    return cast(
        models.GigyaTfaEmailCompleteVerificationResponse,
        await request(
            websession,
            "GET",
            f"{root_url}/accounts.tfa.email.completeVerification",
            params={
                "APIKey": api_key,
                "gigyaAssertion": gigya_assertion,
                "phvToken": phv_token,
                "code": code,
            },
            schema=schemas.GigyaTfaEmailCompleteVerificationResponseSchema,
            cookies=device_ids,
        ),
    )


async def finalize_tfa(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    *,
    device_ids: dict[str, str],
    gigya_assertion: str,
    provider_assertion: str,
    reg_token: str,
    remember_device: bool = True,
) -> None:
    """Send GET to /accounts.tfa.finalizeTFA to complete the TFA challenge.

    Afterwards, call `login` again with the same credentials to obtain the
    now-valid Gigya login token; `finalizeTFA` itself does not return one.
    `remember_device` maps to Gigya's `tempDevice` flag (inverted): when
    `True`, the device is remembered for future logins (no repeat TFA for
    about 30 days), matching Gigya's own web client default.
    """
    await request(
        websession,
        "GET",
        f"{root_url}/accounts.tfa.finalizeTFA",
        params={
            "APIKey": api_key,
            "gigyaAssertion": gigya_assertion,
            "providerAssertion": provider_assertion,
            "regToken": reg_token,
            "tempDevice": str(not remember_device).lower(),
        },
        schema=schemas.GigyaResponseSchema,
        cookies=device_ids,
    )
