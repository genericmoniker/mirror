"""Step count from the Fitbit API."""

import asyncio
import logging
import secrets
from asyncio import create_task
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urlencode

import httpx
from httpx import TransportError

from mirror.plugin_context import PluginContext

from .fitbit import AUTHORIZATION_URL, CredentialsError, get_access_token, get_activity

# A forum post said that devices tend to sync every 15 minutes when in range of a phone.
REFRESH_INTERVAL = timedelta(minutes=15)

# database keys per person:
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
AUTHORIZATION_CODE = "authorization_code"
ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"

STATE_MAP = "state"

REDIRECT_URI = "http://localhost:5000/oauth/activity"

_logger = logging.getLogger(__name__)


@dataclass
class _State:
    wake_event: asyncio.Event = field(default_factory=asyncio.Event)
    task: asyncio.Task | None = None


_state: _State = _State()


def start_plugin(context: PluginContext) -> None:
    _state.task = create_task(_refresh(context), name="activity.refresh")


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    if _state.task:
        _state.task.cancel()


async def set_authorization_code(context: PluginContext, code: str, state: str) -> None:
    # Figure out which person this is for, then fetch the access token.
    state_map = context.db.get(STATE_MAP, {})
    if not state_map:
        _logger.error("OAuth state map is empty.")
        return
    name = state_map.pop(state, None)
    if not name:
        _logger.error("OAuth state not found: %s", state)
        return
    creds = _get_creds(context, name)
    async with httpx.AsyncClient(timeout=10) as client:
        access_token, refresh_token = await get_access_token(
            client,
            code,
            creds[CLIENT_ID],
            creds[CLIENT_SECRET],
            redirect_uri=REDIRECT_URI,
        )
        creds[ACCESS_TOKEN] = access_token
        creds[REFRESH_TOKEN] = refresh_token
        _logger.info("Authorization successful for %s", name)
        context.db[name] = creds
        context.db[STATE_MAP] = state_map
        # Wake up the loop in _refresh() to fetch new data:
        _wake_refresh_loop()


def _get_creds(context: PluginContext, name: str) -> dict:
    """Get the saved credentials for a person by name.

    The credentials are fetched from the database and updated with the client ID and
    client secret from the plugin configuration (mirror.toml).
    """
    creds = context.db.get(name, {})
    config = next(item for item in context.config if item["name"] == name)
    creds |= {
        CLIENT_ID: config[CLIENT_ID],
        CLIENT_SECRET: config[CLIENT_SECRET],
    }
    return creds


async def _refresh(context: PluginContext) -> None:
    """Get the step count data."""
    names = sorted(item["name"] for item in context.config)
    data = {
        "persons": [
            {"name": name, "steps_goal": 0, "steps": 0, "percent": 0.0}
            for name in names
        ],
    }
    event = _state.wake_event
    while True:
        try:
            for_date = datetime.now().astimezone()
            for i, name in enumerate(names):
                person = data["persons"][i]
                creds = _get_creds(context, name)
                try:
                    activity_data = await get_activity(creds, for_date)
                    person["login_required"] = False
                except CredentialsError as ex:
                    _logger.warning("Credentials problem for %s: %s", name, ex)
                    person["login_required"] = True
                    person["auth_url"] = _get_auth_url(context, name)
                    continue
                context.db[name] = creds  # potentially update creds
                person["steps_goal"] = activity_data["goals"]["steps"]
                person["steps"] = activity_data["summary"]["steps"]
                person["percent"] = person["steps"] / person["steps_goal"]
                _logger.info(
                    "%s steps goal: %s, steps: %s (%s%%)",
                    name,
                    person["steps_goal"],
                    person["steps"],
                    round(person["percent"] * 100, 2),
                )
            await context.widget_updated(data)
            context.vote_connected()
        except TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error updating activity data.")
        except Exception:
            _logger.exception("Error updating activity data.")

        # Wait for the next refresh interval, or until the wake event is set.
        try:
            await asyncio.wait_for(
                event.wait(),
                timeout=REFRESH_INTERVAL.total_seconds(),
            )
        except TimeoutError:
            pass
        finally:
            event.clear()


def _wake_refresh_loop() -> None:
    """Wake up the refresh loop immediately."""
    _state.wake_event.set()


def _get_auth_url(context: PluginContext, name: str) -> str:
    """Get the authorization URL for a person by name."""
    # Generate a unique state for this request and store it in the database so that we
    # can verify it when the user is redirected back to us, and know which person it
    # is for.
    state = secrets.token_urlsafe(16)
    state_map = context.db.get(STATE_MAP, {})
    state_map[state] = name
    context.db[STATE_MAP] = state_map

    creds = _get_creds(context, name)
    params = {
        "response_type": "code",
        "scope": "activity",
        "client_id": creds[CLIENT_ID],
        "state": state,
        "redirect_uri": REDIRECT_URI,
    }
    return AUTHORIZATION_URL + "?" + urlencode(params)
