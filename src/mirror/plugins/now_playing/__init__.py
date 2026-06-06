"""Plugin to show the currently playing track on a Spotify Premium account.

Spotify authorization guide:
https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
"""

import asyncio
import base64
import contextlib
import json
import logging
import secrets
from asyncio import create_task, sleep
from datetime import timedelta
from urllib.parse import urlencode

import httpx2

from mirror.errors import AuthError
from mirror.plugin_context import PluginContext

API_URL = "https://api.spotify.com/"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-currently-playing"
REDIRECT_URI = "http://127.0.0.1:5000/oauth/now_playing"  # http requires loopback IP

REFRESH_INTERVAL = timedelta(seconds=30)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context: PluginContext) -> None:
    if not context.config.get("client_id"):
        _logger.info("Plugin not configured (missing client_id in config).")
        return
    task = create_task(_refresh(context), name="now_playing.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def set_authorization_code(context: PluginContext, code: str, state: str) -> None:
    stored_state = context.db.get("oauth_state")
    if not stored_state or stored_state != state:
        raise AuthError("OAuth state mismatch for now_playing.")
    client_id = context.config["client_id"]
    client_secret = context.config["client_secret"]
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    async with httpx2.AsyncClient(timeout=10) as client:
        response = await client.post(
            TOKEN_URL,
            headers={"Authorization": f"Basic {credentials}"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
        )
        response.raise_for_status()
        token = response.json()
    context.db["token"] = json.dumps(token)
    del context.db["oauth_state"]
    _logger.info("Spotify authorization successful.")
    _wake_refresh_loop()


def _get_auth_url(context: PluginContext) -> str:
    state = context.db.get("oauth_state")
    if not state:
        state = secrets.token_urlsafe(16)
        context.db["oauth_state"] = state
    params = {
        "response_type": "code",
        "client_id": context.config["client_id"],
        "scope": SCOPE,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "show_dialog": "true",
    }
    return AUTH_URL + "?" + urlencode(params)


def _wake_refresh_loop() -> None:
    event = _state.get("wake_event")
    if event:
        event.set()


async def _refresh(context: PluginContext) -> None:
    wake_event = asyncio.Event()
    _state["wake_event"] = wake_event
    while True:
        sleep_time = REFRESH_INTERVAL.total_seconds()
        try:
            if not context.db.get("token"):
                auth_url = _get_auth_url(context)
                await context.widget_updated(
                    {"login_required": True, "auth_url": auth_url}
                )
                await sleep(sleep_time)
                continue
            response = await _get_currently_playing(context)
            data = _transform_currently_playing_track(response)
            await context.widget_updated(data)
            context.vote_connected()
            sleep_time = _get_next_poll_seconds(data)
        except httpx2.TransportError as ex:
            context.vote_disconnected(ex)
            _logger.exception("Network error getting now playing data.")
        except httpx2.HTTPStatusError as ex:
            if ex.response.status_code == 401:  # noqa: PLR2004
                # If we get here, it means that trying to use the refresh token failed.
                # Clear the token to require reauthorization.
                _logger.warning("Spotify needs reauthorization.")
                context.db.pop("token", None)
            else:
                _logger.exception("HTTP error getting now playing data.")
        except Exception:
            _logger.exception("Error getting now playing data.")
        _logger.debug("sleep time: %s", sleep_time)
        wake_event.clear()
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(wake_event.wait(), timeout=sleep_time)


async def _get_currently_playing(context: PluginContext) -> httpx2.Response:
    token: dict[str, str] = json.loads(context.db["token"])
    client_id = context.config["client_id"]
    client_secret = context.config["client_secret"]
    url = API_URL + "v1/me/player/currently-playing"
    async with httpx2.AsyncClient(timeout=10) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        if response.status_code == 401:  # noqa: PLR2004
            token = await _refresh_token(client, token, client_id, client_secret)
            context.db["token"] = json.dumps(token)
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token['access_token']}"},
            )
        return response


async def _refresh_token(
    client: httpx2.AsyncClient,
    token: dict[str, str],
    client_id: str,
    client_secret: str,
) -> dict:
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    response = await client.post(
        TOKEN_URL,
        headers={"Authorization": f"Basic {credentials}"},
        data={
            "grant_type": "refresh_token",
            "refresh_token": token["refresh_token"],
        },
    )
    response.raise_for_status()
    new_token = response.json()
    if "refresh_token" not in new_token:
        new_token["refresh_token"] = token["refresh_token"]
    return new_token


def _transform_currently_playing_track(response: httpx2.Response) -> dict:
    """Create a simplified view of the currently playing track."""
    response.raise_for_status()

    if response.status_code == 204:  # noqa: PLR2004
        # Nothing playing right now.
        return {}

    raw = response.json()

    # When something is playing, the "item" object may be:
    # 1. None, which is currently the case for audio books -- no API support for info.
    # 2. A track object for music information.
    # 3. An episode object for podcast information.
    item = raw.get("item")
    if not item:
        return {}

    return {
        "name": item["name"],
        "artists": [artist["name"] for artist in item["artists"]],
        "duration_ms": item["duration_ms"],
        "progress_ms": raw["progress_ms"],
        "is_playing": raw["is_playing"],  # May be paused at the moment if False.
    }


def _get_next_poll_seconds(data: dict[str, int]) -> float:
    """Get the number of seconds until the next poll.

    This attempts to catch track changes right away.
    """
    if not data or not data.get("is_playing"):
        return REFRESH_INTERVAL.total_seconds()
    duration_ms = data["duration_ms"]
    progress_ms = data["progress_ms"]
    track_finished_seconds = ((duration_ms - progress_ms) / 1000) + 1
    return min(track_finished_seconds, REFRESH_INTERVAL.total_seconds())
