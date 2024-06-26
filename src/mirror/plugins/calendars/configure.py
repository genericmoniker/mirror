"""Calendars plugin configuration."""

# TODO: Maybe PyInquirer for this?
# https://github.com/CITGuru/PyInquirer
# Or prompt_toolkit/textual for a TUI?

# TODO: How do you indicate you want to clear a value in a simple prompt with a default?

# Google API Console (client credentials)
# https://console.developers.google.com/

import json
from pathlib import Path

from mirror.plugin_configure_context import PluginConfigureContext

from .common import (
    CLIENT_CREDENTIALS,
    COMING_UP_FILTER,
    SUBORDINATE_FILTER,
    USER_CREDENTIALS,
)
from .google_calendar import obtain_user_permission


def configure_plugin(config_context: PluginConfigureContext) -> None:
    db = config_context.db
    print("Calendar Plugin Set Up")

    client_creds = _configure_client_credentials(db)
    _configure_user_credentials(db, client_creds)
    _configure_coming_up_filter(db)
    _configure_subordinate_calendars(db)


def _configure_client_credentials(db: dict) -> dict:
    client_creds = db.get(CLIENT_CREDENTIALS)
    if client_creds:
        prompt = "Path to credentials.json [keep existing credentials]: "
    else:
        prompt = "Path to credentials.json: "

    success = False
    while not success:
        response = input(prompt).strip()
        if not response and client_creds:
            break  # Keep the existing credentials.
        path = Path(response)
        try:
            client_creds = json.loads(path.read_bytes())["installed"]
            db[CLIENT_CREDENTIALS] = client_creds
            db[USER_CREDENTIALS] = {}
            success = True
        except Exception as ex:  # noqa: BLE001
            print(ex)

    return client_creds


def _configure_user_credentials(db: dict, client_creds: dict) -> None:
    user_creds = db.get(USER_CREDENTIALS)
    if user_creds:
        response = input("Reset user permission? [y/N] ")
        if response in ("y", "Y", "yes", "YES"):
            user_creds = None
    if not user_creds:
        print("Launching browser to obtain user permission...")
        user_creds = obtain_user_permission(client_creds)
        db[USER_CREDENTIALS] = user_creds


def _configure_coming_up_filter(db: dict) -> None:
    """Prompt for a regex filter that excludes coming up events on match."""
    filter_regex = db.get(COMING_UP_FILTER)
    response = input(f"Coming up regex filter [{filter_regex}]: ").strip()
    if response:
        db[COMING_UP_FILTER] = response


def _configure_subordinate_calendars(db: dict) -> None:
    """Prompt for a regex that makes events with matching calendar names subordinate."""
    filter_regex = db.get(SUBORDINATE_FILTER)
    response = input(f"Subordinate calendar regex filter [{filter_regex}]: ").strip()
    if response:
        db[SUBORDINATE_FILTER] = response
