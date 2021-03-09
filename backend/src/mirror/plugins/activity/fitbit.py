"""Activity data from the Fitbit API.

A note on "creds" parameters:

The dict is expected to have these keys:
    - client_id
    - client_secret
    - authorization_code

It may also have these keys, and they may be updated during function calls:
    - access_token
    - refresh_token
"""
from base64 import b64encode
from datetime import datetime

import httpx


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


async def get_activity(creds: dict, for_date: datetime) -> dict:
    """Get activity data for the given date."""
    date = for_date.strftime("%Y-%m-%d")
    url_path = f"activities/date/{date}.json"
    return await _api_request(creds, url_path)


async def _api_request(creds: dict, url_path: str) -> dict:
    if not creds:
        raise CredentialsError
    async with httpx.AsyncClient() as client:
        if not creds.get("access_token"):
            await _get_access_token(client, creds)
        url = "https://api.fitbit.com/1/user/-/" + url_path
        try:
            return await _do_resource_get(client, creds, url)
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == 401:
                try:
                    await _refresh_access_token(client, creds)
                    return await _do_resource_get(client, creds, url)
                except httpx.HTTPStatusError as ex:
                    if ex.response.status_code == 401:
                        raise CredentialsError from ex
                    raise
            raise


async def _get_access_token(client, creds: dict) -> None:
    """Exchange an authorization code for an access token and refresh token.

    https://dev.fitbit.com/build/reference/web-api/oauth2/#access_token-request
    """
    post_data = {
        "code": creds["authorization_code"],
        "grant_type": "authorization_code",
        "redirect_uri": "http://localhost:5000/fitbit",
    }
    data = await _do_auth_post(client, creds, post_data)
    creds["access_token"] = data["access_token"]
    creds["refresh_token"] = data["refresh_token"]


async def _refresh_access_token(client, creds: dict) -> None:
    """Exchange a refresh token for a new access token and refresh token.

    https://dev.fitbit.com/build/reference/web-api/oauth2/#refreshing-tokens
    """
    post_data = {
        "refresh_token": creds["refresh_token"],
        "grant_type": "refresh_token",
    }
    data = await _do_auth_post(client, creds, post_data)
    creds["access_token"] = data["access_token"]
    creds["refresh_token"] = data["refresh_token"]


async def _do_resource_get(client, creds: dict, url) -> dict:
    """Make a GET to the resource server."""
    headers = {"Authorization": "Bearer " + creds["access_token"]}
    response = await client.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


async def _do_auth_post(client, creds: dict, post_data: dict) -> dict:
    """Make a POST to the authorization server."""
    url = "https://api.fitbit.com/oauth2/token"
    auth_value = b64encode(f"{creds['client_id']}:{creds['client_secret']}".encode())
    headers = {"Authorization": "Basic " + auth_value.decode()}
    response = await client.post(url, headers=headers, data=post_data)
    response.raise_for_status()
    return response.json()
