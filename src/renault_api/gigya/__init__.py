"""Gigya API."""

import logging
from json import JSONDecodeError
from typing import Any
from typing import cast

import aiohttp
from marshmallow.schema import Schema
from yarl import URL

from . import models
from . import schemas
from .exceptions import GigyaException

GIGYA_JWT = "gigya_jwt"
GIGYA_LOGIN_TOKEN = "gigya_login_token"  # nosec
GIGYA_PERSON_ID = "gigya_person_id"
GIGYA_KEYS = [GIGYA_JWT, GIGYA_LOGIN_TOKEN, GIGYA_PERSON_ID]

_LOGGER = logging.getLogger(__name__)


async def request(
    websession: aiohttp.ClientSession,
    method: str,
    url: str,
    data: dict[str, Any],
    schema: Schema,
    params: dict[str, Any] | None = None,
) -> models.GigyaResponse:
    """Send request to Gigya."""
    async with websession.request(
        method, url, data=data, params=params
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
    login_id: str,
    password: str,
) -> models.GigyaLoginResponse:
    """Send POST to /accounts.login."""
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


async def _get_tfa_bootstrap_cookies(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
) -> dict[str, str]:
    """Send GET to /accounts.webSdkBootstrap and return the resulting cookies.

    The two-factor-authentication endpoints below require the `ucid`/`gmid`
    cookies set by this call to also be sent back as query parameters.
    """
    async with websession.request(
        "GET",
        f"{root_url}/accounts.webSdkBootstrap",
        params={"APIKey": api_key},
    ) as http_response:
        http_response.raise_for_status()

    jar_cookies = websession.cookie_jar.filter_cookies(URL(root_url))
    return {
        name: jar_cookies[name].value
        for name in ("ucid", "gmid")
        if name in jar_cookies
    }


async def init_tfa(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    reg_token: str,
) -> models.GigyaTfaInitResponse:
    """Send GET to /accounts.tfa.initTFA to start an email one-time-code challenge.

    `reg_token` comes from `PendingTwoFactorAuthenticationException.reg_token`,
    raised by `login` when the account requires two-factor authentication.
    """
    cookies = await _get_tfa_bootstrap_cookies(websession, root_url, api_key)
    return cast(
        models.GigyaTfaInitResponse,
        await request(
            websession,
            "GET",
            f"{root_url}/accounts.tfa.initTFA",
            data={},
            params={
                "APIKey": api_key,
                "regToken": reg_token,
                "provider": "gigyaEmail",
                "mode": "verify",
                **cookies,
            },
            schema=schemas.GigyaTfaInitResponseSchema,
        ),
    )


async def get_tfa_emails(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_assertion: str,
) -> models.GigyaTfaEmailListResponse:
    """Send GET to /accounts.tfa.email.getEmails to list the emails eligible for TFA."""
    return cast(
        models.GigyaTfaEmailListResponse,
        await request(
            websession,
            "GET",
            f"{root_url}/accounts.tfa.email.getEmails",
            data={},
            params={"APIKey": api_key, "gigyaAssertion": gigya_assertion},
            schema=schemas.GigyaTfaEmailListResponseSchema,
        ),
    )


async def send_tfa_email_code(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_assertion: str,
    email_id: str,
) -> models.GigyaTfaSendEmailCodeResponse:
    """Send GET to /accounts.tfa.email.sendVerificationCode to email the OTP code."""
    return cast(
        models.GigyaTfaSendEmailCodeResponse,
        await request(
            websession,
            "GET",
            f"{root_url}/accounts.tfa.email.sendVerificationCode",
            data={},
            params={
                "APIKey": api_key,
                "gigyaAssertion": gigya_assertion,
                "emailID": email_id,
            },
            schema=schemas.GigyaTfaSendEmailCodeResponseSchema,
        ),
    )


async def complete_tfa_email_verification(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
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
            data={},
            params={
                "APIKey": api_key,
                "gigyaAssertion": gigya_assertion,
                "phvToken": phv_token,
                "code": code,
            },
            schema=schemas.GigyaTfaEmailCompleteVerificationResponseSchema,
        ),
    )


async def finalize_tfa(
    websession: aiohttp.ClientSession,
    root_url: str,
    api_key: str,
    gigya_assertion: str,
    provider_assertion: str,
    reg_token: str,
    *,
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
        data={},
        params={
            "APIKey": api_key,
            "gigyaAssertion": gigya_assertion,
            "providerAssertion": provider_assertion,
            "regToken": reg_token,
            "tempDevice": str(not remember_device).lower(),
        },
        schema=schemas.GigyaResponseSchema,
    )
