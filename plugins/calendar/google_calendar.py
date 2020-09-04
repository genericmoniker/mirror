"""Data from Google Calendar.

Google API reference:
https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
"""

import logging
import threading

from google.auth.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery

SCOPES = "https://www.googleapis.com/auth/calendar.readonly"


_logger = logging.getLogger(__name__)
_credentials_lock = threading.Lock()


def obtain_user_permission(client_creds) -> Credentials:
    flow = InstalledAppFlow.from_client_config(client_creds, SCOPES)
    return flow.run_local_server(port=0)



def credentials_to_dict(credentials: Credentials) -> dict:
    return dict(
        token=credentials.token,
        refresh_token=credentials.refresh_token,
        id_token=credentials.id_token,
        token_uri=credentials.token_uri,
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scopes=credentials.scopes,
    )


def credentials_from_dict(d: dict) -> Credentials:
    return Credentials(**d)



def no_filter(_event):
    """An event filter that doesn't filter out any events."""
    return True


def get_calendar_data(list_args, filter_func=no_filter):
    """List events from all calendars according to the parameters given.

    :param list_args: Arguments to pass to the calendar API's event list
        function.
    :param filter_func: Callable that can filter out individual events.
        The function should return True to include, False to exclude.
    """
    credentials = get_credentials()
    service = discovery.build(
        "calendar", "v3", credentials=credentials, cache=DiscoveryCache()
    )
    calendar_list = service.calendarList().list().execute()
    events = []
    for calendar_list_entry in calendar_list["items"]:
        calendar_id = calendar_list_entry["id"]
        try:
            events_result = (
                service.events()
                .list(calendarId=calendar_id, singleEvents=True, **list_args)
                .execute()
            )
        except HttpError as ex:
            logger.error(
                'Error getting events from "%s". %s',
                calendar_list_entry["summary"],
                ex,
            )
        else:
            events += [e for e in events_result.get("items", []) if filter_func(e)]
    return dict(items=sorted(events, key=event_sort_key_function))


class DiscoveryCache:
    """Cache for Google service discovery.

    See https://github.com/googleapis/google-api-python-client/issues/325
    """

    def __init__(self) -> None:
        self._cache = {}

    def get(self, url):
        return self._cache.get(url)

    def set(self, url, content):
        self._cache[url] = content


def get_credentials():
    with CREDENTIALS_LOCK:
        err = (
            "Error loading Google credentials from {}. "
            "Run agenda.py to generate a new credentials file. Problem: ".format(
                CREDENTIALS_PATH
            )
        )
        if not CREDENTIALS_PATH.exists():
            raise Exception(err + "File does not exist.")
        try:
            credentials = pickle.loads(CREDENTIALS_PATH.read_bytes())
        except Exception as e:
            raise Exception(err + "Error un-pickling.") from e
        if not credentials:
            raise Exception(err + "No data un-pickled.")
        if not credentials.valid and not credentials.expired:
            raise Exception(err + "Credentials invalid but not expired.")
        if not credentials.valid and not credentials.refresh_token:
            raise Exception(err + "Credentials expired but no refresh token.")
        if not credentials.valid:
            logger.info("Refreshing Google credentials.")
            credentials.refresh(Request())
        CREDENTIALS_PATH.write_bytes(pickle.dumps(credentials))
        return credentials


def event_sort_key_function(event):
    start = event.get("start", {})
    # start may be specified by either 'date' or 'dateTime'
    return start.get("date", start.get("dateTime", ""))
