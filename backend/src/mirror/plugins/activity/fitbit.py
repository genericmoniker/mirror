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
import logging
from base64 import b64encode
from datetime import datetime

import httpx

_logger = logging.getLogger(__name__)


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


async def get_activity(creds: dict, for_date: datetime) -> dict:
    """Get activity data for the given date."""
    date = for_date.strftime("%Y-%m-%d")
    url_path = f"activities/date/{date}.json"
    return await _api_request(creds, url_path)

    # Use this instead of _api_request for testing:
    # return _get_activity_test_data()


def _get_activity_test_data():
    """Get sample data for testing w/o authenticating to the Fitbit API."""
    import json  # pylint:disable=import-outside-toplevel
    import random  # pylint:disable=import-outside-toplevel
    from pathlib import Path  # pylint:disable=import-outside-toplevel

    root_dir = Path(__file__).parent.parent.parent.parent.parent.parent
    data = (root_dir / ".data_samples/fitbit-activity.json").read_text()
    data = json.loads(data)
    data["summary"]["steps"] = random.randint(0, 10_000)
    return data


async def _api_request(creds: dict, url_path: str) -> dict:
    if not creds:
        raise CredentialsError
    async with httpx.AsyncClient(timeout=10) as client:
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
    if response.is_error:
        _logger.error(response.content)
    response.raise_for_status()
    return response.json()
