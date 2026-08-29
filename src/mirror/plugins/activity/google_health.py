"""Activity data from the Google Health API.

https://developers.google.com/health/reference/rest
"""

from base64 import b64encode
from datetime import datetime

import httpx2

AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = ["https://www.googleapis.com/auth/googlehealth.activity_and_fitness.readonly"]

_API_BASE = "https://health.googleapis.com/v4/users/me"


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


async def get_activity(creds: dict, for_date: datetime) -> dict:
    """Get step count for the given date or raise CredentialsError."""
    if not creds.get("access_token"):
        msg = "No access token found in credentials."
        raise CredentialsError(msg)
    civil_date = {"year": for_date.year, "month": for_date.month, "day": for_date.day}
    body = {
        "range": {
            "start": {"date": civil_date, "time": {"hours": 0}},
            "end": {
                "date": civil_date,
                "time": {"hours": 23, "minutes": 59, "seconds": 59},
            },
        },
        "windowSizeDays": 1,
    }
    url = f"{_API_BASE}/dataTypes/steps/dataPoints:dailyRollUp"
    async with httpx2.AsyncClient(timeout=10) as client:
        try:
            data = await _do_api_post(client, creds["access_token"], url, body)
        except httpx2.HTTPStatusError as ex:
            if ex.response.status_code == 401:  # noqa: PLR2004
                try:
                    access_token = await _refresh_access_token(client, creds)
                    data = await _do_api_post(client, access_token, url, body)
                except httpx2.HTTPStatusError as ex2:
                    raise CredentialsError(ex2.response.json()) from ex2
            else:
                raise
    points = data.get("rollupDataPoints", [])
    steps = int(points[0]["steps"]["countSum"]) if points else 0
    return {"steps": steps}


async def get_access_token(
    client: httpx2.AsyncClient,
    authorization_code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> tuple[str, str]:
    """Exchange an authorization code for an access token and refresh token."""
    data = await _do_token_post(
        client,
        client_id,
        client_secret,
        {
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    return data["access_token"], data["refresh_token"]


async def _refresh_access_token(client: httpx2.AsyncClient, creds: dict) -> str:
    # Google does not reissue the refresh token; only update the access token.
    data = await _do_token_post(
        client,
        creds["client_id"],
        creds["client_secret"],
        {
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token",
        },
    )
    creds["access_token"] = data["access_token"]
    return data["access_token"]


async def _do_api_post(
    client: httpx2.AsyncClient,
    access_token: str,
    url: str,
    body: dict,
) -> dict:
    headers = {"Authorization": "Bearer " + access_token}
    response = await client.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()


async def _do_token_post(
    client: httpx2.AsyncClient,
    client_id: str,
    client_secret: str,
    post_data: dict,
) -> dict:
    auth_value = b64encode(f"{client_id}:{client_secret}".encode())
    headers = {"Authorization": "Basic " + auth_value.decode()}
    response = await client.post(TOKEN_URL, headers=headers, data=post_data)
    response.raise_for_status()
    return response.json()
