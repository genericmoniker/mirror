"""Agenda data from Google Calendar.

Google API reference:
https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
"""
import datetime
import logging
import pickle
import re
import threading
from functools import partial
from pathlib import Path

import tzlocal
from flask import current_app
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from googleapiclient.errors import HttpError

from cache import Cache

logger = logging.getLogger(__name__)

SCOPES = "https://www.googleapis.com/auth/calendar.readonly"
APPLICATION_NAME = "Magic Mirror"
HERE = Path(__file__).parent
CREDENTIALS_PATH = HERE / "instance" / "google_token.pickle"
CREDENTIALS_LOCK = threading.Lock()
CLIENT_SECRET_PATH = HERE / "instance" / "google_client_id.json"
AGENDA_REFRESH_MINUTES = 5
COMING_UP_REFRESH_MINUTES = 10
COUNTDOWN_REFRESH_MINUTES = 20

agenda_cache = None
coming_up_cache = None
countdown_cache = None


def init_cache(_config, scheduler):
    global agenda_cache, coming_up_cache, countdown_cache

    agenda_cache = Cache(
        scheduler,
        "Refresh Agenda",
        AGENDA_REFRESH_MINUTES,
        partial(get_agenda_data, get_agenda_event_range),
    )
    coming_up_cache = Cache(
        scheduler,
        "Refresh Coming Up",
        COMING_UP_REFRESH_MINUTES,
        partial(get_agenda_data, get_coming_up_event_range, coming_up_filter),
    )
    countdown_cache = Cache(
        scheduler, "Refresh Countdown", COUNTDOWN_REFRESH_MINUTES, get_countdown_data,
    )


def get_agenda():
    """Get the agenda for the current day."""
    assert agenda_cache, "init_cache must be called first!"
    return agenda_cache.get()


def get_coming_up():
    """Get all-day events in the next week."""
    assert coming_up_cache, "init_cache must be called first!"
    return coming_up_cache.get()


def get_countdown():
    """Get events tagged in the calendar for long-term countdowns.

    This includes future events with "mirror-countdown" in them.
    """
    assert countdown_cache, "init_cache must be called first!"
    return countdown_cache.get()


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


def no_filter(_event):
    return True


def coming_up_filter(event):
    # All day events only have a date, not a dateTime.
    if "dateTime" in event["start"]:
        return False
    # For multi-day events, skip them if they've already started.
    start = parse_date_tz(event["start"]["date"])
    if start <= start_of_day_tz():
        return False
    # Check any custom filters from the config.
    pattern = current_app.config.get("COMING_UP_FILTER")
    if pattern and re.match(pattern, event["summary"]):
        return False

    return True


def get_agenda_data(range_func, filter_func=no_filter):
    start, stop = range_func()
    list_args = {"timeMin": start, "timeMax": stop}
    return get_calendar_data(list_args, filter_func)


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


def get_coming_up_event_range():
    """Get times from tomorrow until a week from today."""
    start = start_of_day_tz() + datetime.timedelta(days=1)
    stop = end_of_day_tz() + datetime.timedelta(days=6)
    logger.info("coming up range: %s - %s", start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()


def event_sort_key_function(event):
    start = event.get("start", {})
    # start may be specified by either 'date' or 'dateTime'
    return start.get("date", start.get("dateTime", ""))


def get_countdown_data():
    start = (end_of_day_tz() + datetime.timedelta(days=7)).isoformat()
    query = "mirror-countdown"
    list_args = {"timeMin": start, "q": query}
    return get_calendar_data(list_args)


def get_user_permission():
    """Run through the OAuth flow to get credentials."""
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_PATH), SCOPES)
    credentials = flow.run_local_server(port=0)
    CREDENTIALS_PATH.write_bytes(pickle.dumps(credentials))


if __name__ == "__main__":
    get_user_permission()
