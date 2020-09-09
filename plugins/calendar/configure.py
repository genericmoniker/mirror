# TODO: Maybe PyInquirer for this?
# https://github.com/CITGuru/PyInquirer

# TODO:
# How do you indicate you want to clear a value in a simple prompt with a default?

# Google API Console (client credentials)
# https://console.developers.google.com/

import json
from pathlib import Path

from .common import CLIENT_CREDENTIALS, COMING_UP_FILTER, USER_CREDENTIALS
from .google_calendar import obtain_user_permission


def configure_plugin(db):
    print("Calendar Plugin Set Up")

    client_creds = _configure_client_credentials(db)
    _configure_user_credentials(db, client_creds)
    _configure_coming_up_filter(db)


def _configure_client_credentials(db):
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
            client_creds = json.loads(path.read_bytes())
            db[CLIENT_CREDENTIALS] = client_creds
            success = True
        except Exception as e:
            print(e)

    return client_creds


def _configure_user_credentials(db, client_creds):
    user_creds = db.get(USER_CREDENTIALS)
    if not user_creds:
        print("Launching browser to obtain user permission...")
        user_creds = obtain_user_permission(client_creds)
        db[USER_CREDENTIALS] = user_creds


def _configure_coming_up_filter(db):
    filter_regex = db.get(COMING_UP_FILTER)
    response = input(f"Coming up regex filter [{filter_regex}]: ").strip()
    if response:
        db[COMING_UP_FILTER] = response
