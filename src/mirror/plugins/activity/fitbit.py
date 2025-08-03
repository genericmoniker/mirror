"""Activity data from the Fitbit API.

https://dev.fitbit.com/build/reference/web-api/

A note on "creds" parameters:

The dict is expected to have these keys:
    - client_id
    - client_secret
    - authorization_code

It may also have these keys, and they may be updated during function calls:
    - access_token
    - refresh_token
"""

import json
import random
from base64 import b64encode
from datetime import datetime
from pathlib import Path

import httpx

AUTHORIZATION_URL = "https://www.fitbit.com/oauth2/authorize"


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


async def get_activity(creds: dict, for_date: datetime) -> dict:
    """Get activity data for the given date or raise CredentialsError."""
    # Set to True for manual testing:
    manual_test = False
    if manual_test:
        return _get_activity_test_data()

    # Otherwise get the real data from the Fitbit API.
    date = for_date.strftime("%Y-%m-%d")
    url_path = f"activities/date/{date}.json"
    return await _api_request(creds, url_path)


def _get_activity_test_data() -> dict:
    """Get sample data for testing w/o authenticating to the Fitbit API."""
    root_dir = Path(__file__).parent.parent.parent.parent.parent
    data_str = (root_dir / ".data_samples/fitbit-activity.json").read_text()
    data = json.loads(data_str)
    data["summary"]["steps"] = random.randint(0, 10_000)  # noqa: S311
    return data


async def _api_request(creds: dict, url_path: str) -> dict:
    if not creds:
        raise CredentialsError
    access_token = creds.get("access_token", "")
    if not access_token:
        msg = "No access token found in credentials."
        raise CredentialsError(msg)
    async with httpx.AsyncClient(timeout=10) as client:
        url = "https://api.fitbit.com/1/user/-/" + url_path
        try:
            return await _do_resource_get(client, access_token, url)
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 401:  # noqa: PLR2004
                try:
                    access_token = await _refresh_access_token(client, creds)
                    return await _do_resource_get(client, access_token, url)
                except httpx.HTTPStatusError as ex:
                    raise CredentialsError(ex.response.json()) from ex
            raise


async def get_access_token(
    client: httpx.AsyncClient,
    authorization_code: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
) -> tuple[str, str]:
    """Exchange an authorization code for an access token and refresh token.

    https://dev.fitbit.com/build/reference/web-api/oauth2/#access_token-request
    """
    post_data = {
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    data = await _do_auth_post(client, client_id, client_secret, post_data)
    return data["access_token"], data["refresh_token"]


async def _refresh_access_token(client: httpx.AsyncClient, creds: dict) -> str:
    """Exchange a refresh token for a new access token and refresh token.

    The new tokens are stored in the creds dict and the access token is returned.

    https://dev.fitbit.com/build/reference/web-api/oauth2/#refreshing-tokens
    """
    post_data = {
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token",
    }
    data = await _do_auth_post(
        client,
        creds["client_id"],
        creds["client_secret"],
        post_data,
    )
    creds["access_token"] = data["access_token"]
    creds["refresh_token"] = data["refresh_token"]
    return data["access_token"]


async def _do_resource_get(
    client: httpx.AsyncClient,
    access_token: str,
    url: str,
) -> dict:
    """Make a GET request to the resource server."""
    headers = {"Authorization": "Bearer " + access_token}
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


async def _do_auth_post(
    client: httpx.AsyncClient,
    client_id: str,
    client_secret: str,
    post_data: dict,
) -> dict:
    """Make a POST request to the authorization server."""
    url = "https://api.fitbit.com/oauth2/token"
    auth_value = b64encode(f"{client_id}:{client_secret}".encode())
    headers = {"Authorization": "Basic " + auth_value.decode()}
    response = await client.post(url, headers=headers, data=post_data)
    response.raise_for_status()
    return response.json()
