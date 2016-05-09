# -*- coding: utf-8 -*-

"""Agenda data from Google Calendar.

"""
import datetime
import os

import httplib2
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
CACHE_TIMEOUT = 2 * 60

cache = SimpleCache()


def get_agenda():
    """Get the agenda for the current day."""
    data = cache.get('agenda')
    if data is None:
        data = get_agenda_data()
        cache.set('agenda', data, CACHE_TIMEOUT)
    return data


def get_credentials():
    store = get_credentials_store()
    credentials = store.get()
    # say something helpful if not credentials or credentials.invalid
    return credentials


def get_credentials_store():
    credentials_file = os.path.join(HERE, 'instance', CREDENTIALS)
    return file.Storage(credentials_file)


def get_agenda_data():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    start, stop = get_event_range()
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
        events += events_result.get('items', [])
    return dict(items=sorted(events, key=event_sort_key_function))


def get_event_range():
    start = datetime.datetime.utcnow()
    tomorrow = start + datetime.timedelta(days=1)
    stop = datetime.datetime(
        year=tomorrow.year,
        month=tomorrow.month,
        day=tomorrow.day
    )
    return start.isoformat() + 'Z', stop.isoformat() + 'Z'


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
