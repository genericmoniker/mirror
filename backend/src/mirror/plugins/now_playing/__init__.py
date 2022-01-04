"""
Plugin to show the currently playing track on a Spotify Premium account.

Spotify authorization guide:
https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
"""

import json
import logging
from asyncio import create_task, sleep
from datetime import timedelta
from functools import partial

import httpx
from authlib.integrations.httpx_client import AsyncOAuth2Client

API_URL = "https://api.spotify.com/"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = "user-read-currently-playing"
REDIRECT_URI = "http://localhost:5050/auth"

REFRESH_INTERVAL = timedelta(seconds=30)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context):
    if context.db.get("client_id"):
        _state["task"] = create_task(_refresh(context), name="now_playing.refresh")
    else:
        _logger.info("Plugin not configured.")


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


def configure_plugin(config_context):
    db = config_context.db
    oauth = config_context.oauth
    print("Now Playing Plugin Set Up")
    client_id = input("Spotify app client ID: ").strip()
    client_secret = input("Spotify app client secret: ").strip()

    # FYI - Spotify auth also supports PKCE, which if used doesn't ever require
    # using the client secret.

    try:
        response, state = oauth.authorize(
            AUTH_URL,
            client_id,
            None,
            SCOPE,
            REDIRECT_URI,
            show_dialog=True,
        )
        token = oauth.fetch_token(
            TOKEN_URL, client_id, client_secret, REDIRECT_URI, response, state
        )
        db["client_id"] = client_id
        db["client_secret"] = client_secret
        db["state"] = state
        db["token"] = json.dumps(token)
        print("Authorization succeeded")
    except Exception as ex:  # pylint: disable=broad-except
        print("Authorization failed:", ex)


async def _refresh(context):
    while True:
        sleep_time = REFRESH_INTERVAL.total_seconds()
        try:
            response = await _get_currently_playing(context.db)
            data = _transform_currently_playing_track(response)
            await context.post_event("refresh", data)
            context.vote_connected()
            sleep_time = _get_next_poll_seconds(data)
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting now playing data.")
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Error getting now playing data.")
        _logger.debug("sleep time: %s", sleep_time)
        await sleep(sleep_time)


async def _get_currently_playing(db):
    # We use the OAuth client, which is a subclass of httpx.AsyncClient,
    # to automatically send the authorization header and handle refresh
    # tokens.
    token = json.loads(db["token"])
    update_partial = partial(_update_token, db)
    async with AsyncOAuth2Client(
        client_id=db["client_id"],
        client_secret=db["client_secret"],
        token=token,
        token_endpoint=TOKEN_URL,
        update_token=update_partial,
        timeout=10,
    ) as client:
        url = API_URL + "v1/me/player/currently-playing"
        return await client.get(url)


async def _update_token(db, token, **kwargs):  # pylint: disable=unused-argument
    # update old token
    db["token"] = json.dumps(token)


def _transform_currently_playing_track(response):
    """Create a simplified view of the currently playing track."""
    response.raise_for_status()

    if response.status_code == 204:
        # Nothing playing right now.
        return {}

    raw = response.json()

    return {
        "name": raw["item"]["name"],
        "artists": [artist["name"] for artist in raw["item"]["artists"]],
        "duration_ms": raw["item"]["duration_ms"],
        "progress_ms": raw["progress_ms"],
        "is_playing": raw["is_playing"],
    }


def _get_next_poll_seconds(data):
    """Get the number of seconds until the next poll.

    This attempts to catch track changes right away.
    """
    if not data or not data["is_playing"]:
        return REFRESH_INTERVAL.total_seconds()
    duration_ms = data["duration_ms"]
    progress_ms = data["progress_ms"]
    track_finished_seconds = ((duration_ms - progress_ms) / 1000) + 1
    return min(track_finished_seconds, REFRESH_INTERVAL.total_seconds())
