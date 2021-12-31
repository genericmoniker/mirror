"""
Plugin to show the currently playing track on a Spotify Premium account.

Spotify authorization guide:
https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
"""

import logging
from asyncio import create_task, sleep
from datetime import timedelta

import httpx
from httpx_auth import OAuth2AuthorizationCodePKCE
from httpx_auth.authentication import OAuth2

API_URL = "https://api.spotify.com/"
AUTH_URL = "https://accounts.spotify.com/"
SCOPE = "user-read-currently-playing"
REDIRECT_URI_ENDPOINT = "auth"
REDIRECT_URI_PORT = 5050

REFRESH_INTERVAL = timedelta(seconds=30)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context):
    if context.db.get("client_id"):
        OAuth2.token_cache.tokens = context.db

        _state["task"] = create_task(_refresh(context), name="now_playing.refresh")
    else:
        _logger.info("Plugin not configured.")


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


def configure_plugin(db):

    # httpx_auth thinks logging exceptions AND raising them is a good idea 😠
    httpx_auth_logger = logging.getLogger("httpx_auth")
    httpx_auth_logger.setLevel(logging.CRITICAL)

    print("Now Playing Plugin Set Up")
    client_id = input("Spotify App Client ID: ").strip()
    print("Launching your browser to continue authorization (if needed)...")

    # This is a little awkward. We'll create an auth object with all the necessary
    # parameters to talk to Spotify, slip in db as the storage for tokens, and request
    # a token through the cache in order to save the needed values.
    auth = _create_auth(client_id)
    OAuth2.token_cache.tokens = db
    try:
        OAuth2.token_cache.get_token(
            auth.state, on_missing_token=auth.request_new_token
        )

        # Hang on to the client_id, too, so we can create auth when running the plugin.
        db["client_id"] = client_id

        print("Successfully authorized")
    except Exception as ex:  # pylint: disable=broad-except
        print("Failed to authorize: ", ex)


def _create_auth(client_id):
    auth = OAuth2AuthorizationCodePKCE(
        authorization_url=AUTH_URL + "authorize",
        token_url=AUTH_URL + "api/token",
        client_id=client_id,
        redirect_uri_endpoint=REDIRECT_URI_ENDPOINT,
        redirect_uri_port=REDIRECT_URI_PORT,
        success_display_time=5000,
        scope=SCOPE,
    )
    return auth


async def _refresh(context):
    auth = _create_auth(context.db["client_id"])
    while True:
        try:
            async with httpx.AsyncClient(auth=auth) as client:
                url = API_URL + "v1/me/player/currently-playing"
                response = await client.get(url)
            data = _transform_currently_playing_track(response)
            await context.post_event("refresh", data)
            context.vote_connected()
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting now playing data.")
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Error getting now_playing data.")
        await sleep(REFRESH_INTERVAL.total_seconds())


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
