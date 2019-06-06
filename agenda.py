"""Agenda data from Google Calendar.

Google API reference:
https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
"""
import datetime
import logging
from functools import partial
from pathlib import Path

import httplib2
import tzlocal
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client import client
from oauth2client import file
from oauth2client import tools

from cache import Cache

logger = logging.getLogger(__name__)

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
APPLICATION_NAME = 'Magic Mirror'
HERE = Path(__file__).parent
CREDENTIALS_PATH = HERE / 'instance' / 'google_calendar_creds.json'
CLIENT_SECRET_PATH = HERE / 'instance' / 'google_client_id.json'
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
        'Refresh Agenda',
        AGENDA_REFRESH_MINUTES,
        partial(get_agenda_data, get_agenda_event_range),
    )
    coming_up_cache = Cache(
        scheduler,
        'Refresh Coming Up',
        COMING_UP_REFRESH_MINUTES,
        partial(get_agenda_data, get_coming_up_event_range, coming_up_filter),
    )
    countdown_cache = Cache(
        scheduler,
        'Refresh Countdown',
        COUNTDOWN_REFRESH_MINUTES,
        get_countdown_data,
    )


def get_agenda():
    """Get the agenda for the current day."""
    assert agenda_cache, 'init_cache must be called first!'
    return agenda_cache.get()


def get_coming_up():
    """Get all-day events in the next week."""
    assert coming_up_cache, 'init_cache must be called first!'
    return coming_up_cache.get()


def get_countdown():
    """Get events tagged in the calendar for long-term countdowns.

    This includes future events with "mirror-countdown" in them.
    """
    assert countdown_cache, 'init_cache must be called first!'
    return countdown_cache.get()


def get_credentials():
    store = get_credentials_store()
    credentials = store.get()
    if not credentials:
        raise Exception(
            'No Google Calendar credentials available for agenda. '
            'Check that {} is not missing or corrupt.'.format(CREDENTIALS_PATH)
        )
    if credentials.invalid:
        raise Exception('Google Calendar credentials invalid for agenda.')
    return credentials


def get_credentials_store():
    return file.Storage(str(CREDENTIALS_PATH))


def no_filter(_event):
    return True


def coming_up_filter(event):
    # All day events only have a date, not a dateTime.
    if 'dateTime' in event['start']:
        return False
    # For multi-day events, skip them if they've already started.
    start = parse_date_tz(event['start']['date'])
    return start > start_of_day_tz()


def get_agenda_data(range_func, filter_func=no_filter):
    start, stop = range_func()
    list_args = {'timeMin': start, 'timeMax': stop}
    return get_calendar_data(list_args, filter_func)


def get_calendar_data(list_args, filter_func=no_filter):
    """List events from all calendars according to the parameters given.

    :param list_args: Arguments to pass to the calendar API's event list
        function.
    :param filter_func: Callable that can filter out individual events.
        The function should return True to include, False to exclude.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    calendar_list = service.calendarList().list().execute()
    events = []
    for calendar_list_entry in calendar_list['items']:
        calendar_id = calendar_list_entry['id']
        try:
            events_result = (
                service.events()
                .list(calendarId=calendar_id, singleEvents=True, **list_args)
                .execute()
            )
        except HttpError as ex:
            logger.error(
                'Error getting events from "%s". %s',
                calendar_list_entry['summary'],
                ex,
            )
        else:
            events += [
                e for e in events_result.get('items', []) if filter_func(e)
            ]
    return dict(items=sorted(events, key=event_sort_key_function))


def get_agenda_event_range():
    """Get times from now until the end of the day."""
    start = now_tz()
    stop = end_of_day_tz()
    logger.info('agenda range: %s - %s', start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()


def get_coming_up_event_range():
    """Get times from tomorrow until a week from today."""
    start = start_of_day_tz() + datetime.timedelta(days=1)
    stop = end_of_day_tz() + datetime.timedelta(days=6)
    logger.info(
        'coming up range: %s - %s', start.isoformat(), stop.isoformat()
    )
    return start.isoformat(), stop.isoformat()


def event_sort_key_function(event):
    start = event.get('start', {})
    # start may be specified by either 'date' or 'dateTime'
    return start.get('date', start.get('dateTime', ''))


def get_countdown_data():
    start = (end_of_day_tz() + datetime.timedelta(days=7)).isoformat()
    query = 'mirror-countdown'
    list_args = {'timeMin': start, 'q': query}
    return get_calendar_data(list_args)


def get_user_permission():
    """Run through the OAuth flow to get credentials."""
    store = get_credentials_store()
    flow = client.flow_from_clientsecrets(str(CLIENT_SECRET_PATH), SCOPES)
    flow.user_agent = APPLICATION_NAME
    tools.run_flow(flow, store)


def now_tz():
    """Get the current local time as a time zone aware datetime."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.astimezone()


def start_of_day_tz():
    """Get the start of the current day as a time zone aware datetime."""
    now = now_tz()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day_tz():
    """Get the end of the current day as a time zone aware datetime."""
    now = now_tz()
    return now.replace(hour=23, minute=59, second=59, microsecond=9999)


def parse_date_tz(date):
    """Parse an ISO8601 date string returning a time zone aware datetime.

    If you want parsing of times and time zones, try the dateutil package.
    """
    parsed = datetime.datetime.strptime(date, '%Y-%m-%d')
    tz = tzlocal.get_localzone()
    return tz.localize(parsed)


if __name__ == '__main__':
    get_user_permission()
