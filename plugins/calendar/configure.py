# TODO: Maybe PyInquirer for this?
# https://github.com/CITGuru/PyInquirer

from pathlib import Path
import json

from .google_calendar import obtain_user_permission

CLIENT_CREDENTIALS = 'client-creds'
USER_CREDENTIALS = 'user-creds'


def configure_plugin(db):
    print("Calendar Plugin Set Up")

    client_creds = _configure_client_credentials(db)
    _configure_user_credentials(db, client_creds)


    name = input("What is your name?")
    db["recipient"] = name or "world"


def _configure_client_credentials(db):
    client_creds = db.get(CLIENT_CREDENTIALS)
    if not client_creds:
        success = False
        while not success:
            path = Path(input("Path to credentials.json: "))
            try:
                client_creds = json.loads(path.read_bytes())
                db[CLIENT_CREDENTIALS] = client_creds
                success = True
            except Exception as e:
                print(e)

    return client_creds


def _configure_user_credentials(db, client_creds):
    print('Launching browser to obtain user permission...')
    user_creds = obtain_user_permission(client_creds)
    db[USER_CREDENTIALS] = user_creds.__getstate__()
