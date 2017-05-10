# -*- coding: utf-8 -*-

"""Agenda data from Google Calendar.

"""
import datetime
import os

import httplib2
import tzlocal
from googleapiclient import discovery
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from werkzeug.contrib.cache import SimpleCache

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
APPLICATION_NAME = 'Magic Mirror'
CLIENT_SECRET = 'google_client_id.json'
CREDENTIALS = 'google_calendar_creds.json'
HERE = os.path.dirname(__file__)
AGENDA_CACHE_TIMEOUT = 2 * 60
COMING_UP_CACHE_TIMEOUT = 10 * 60

cache = SimpleCache()


def get_agenda():
    """Get the agenda for the current day."""
    data = cache.get('agenda')
    if data is None:
        data = get_agenda_data(get_agenda_event_range)
        cache.set('agenda', data, AGENDA_CACHE_TIMEOUT)
    return data


def get_coming_up():
    """Get all-day events in the next week."""
    data = cache.get('coming-up')
    if data is None:
        data = get_agenda_data(get_coming_up_event_range, all_day_filter)
        cache.set('coming-up', data, COMING_UP_CACHE_TIMEOUT)
    return data


def get_credentials():
    store = get_credentials_store()
    credentials = store.get()
    # say something helpful if not credentials or credentials.invalid
    return credentials


def get_credentials_store():
    credentials_file = os.path.join(HERE, 'instance', CREDENTIALS)
    return file.Storage(credentials_file)


def no_filter(event):
    return True


def all_day_filter(event):
    # All day events only have a date, not a dateTime.
    return 'date' in event['start']


def get_agenda_data(range_func, filter_func=no_filter):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    start, stop = range_func()
    calendar_list = service.calendarList().list().execute()
    events = []
    for calendar_list_entry in calendar_list['items']:
        calendar_id = calendar_list_entry['id']
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start,
            timeMax=stop,
            singleEvents=True,
        ).execute()
        events += [e for e in events_result.get('items', []) if filter_func(e)]
    return dict(items=sorted(events, key=event_sort_key_function))


def get_agenda_event_range():
    """Get times from now until the end of the day."""
    start = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    tz = tzlocal.get_localzone()
    end_of_day = datetime.datetime.now().replace(
        hour=23, minute=59, second=59, microsecond=999999
    )
    stop = tz.localize(end_of_day).astimezone(tz=datetime.timezone.utc)
    return start.isoformat(), stop.isoformat()


def get_coming_up_event_range():
    """Get times from tomorrow until a week later."""
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
    start = now + datetime.timedelta(days=1)
    stop = start + datetime.timedelta(days=7)
    return start.isoformat(), stop.isoformat()


def event_sort_key_function(event):
    start = event.get('start', {})
    # start may be specified by either 'date' or 'dateTime'
    return start.get('date', start.get('dateTime', ''))


def get_user_permission():
    """Run through the OAuth flow to get credentials."""
    client_id_file = os.path.join(HERE, 'instance', CLIENT_SECRET)
    store = get_credentials_store()
    flow = client.flow_from_clientsecrets(client_id_file, SCOPES)
    flow.user_agent = APPLICATION_NAME
    tools.run_flow(flow, store)


if __name__ == '__main__':
    get_user_permission()
