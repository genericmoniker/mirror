"""Retrieve data from Google Calendar.

Google API references:
https://developers.google.com/calendar/v3/errors?hl=en
https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
"""

import logging

from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import discovery
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


_logger = logging.getLogger(__name__)


def obtain_user_permission(client_creds) -> dict:
    """Run the authorization flow to grant permission to access a user's calendar.

    :return: mapping of user credentials that can be used when calling
        `get_calendar_data`.
    """
    # TODO: What happens if the user declines?
    flow = InstalledAppFlow.from_client_config(client_creds, SCOPES)
    return flow.run_local_server(port=0).__getstate__()


def no_filter(_event):
    """An event filter that doesn't filter out any events."""
    return True


def get_calendar_events(user_creds, list_args, filter_func=None):
    """List events from all calendars according to the parameters given.

    The supplied credentials dict may be updated if tokens are refreshed.

    :param user_creds: User credentials from `obtain_user_permission`.
    :param list_args: Arguments to pass to the calendar API's event list
        function.
    :param filter_func: Callable that can filter out individual events.
        The function should return True to include, False to exclude.
    :raise CredentialsError: if the credentials have not been set up,
        or if they have expired.
    """
    filter_func = filter_func or no_filter
    credentials = _credentials_from_dict(user_creds)
    service = discovery.build(
        "calendar",
        "v3",
        credentials=credentials,
        cache=_DiscoveryCache(),
        num_retries=3,
    )
    try:
        calendar_list = (
            service.calendarList().list().execute()  # pylint: disable=no-member
        )
        events = []
        for calendar_list_entry in calendar_list["items"]:
            _add_calendar_events(
                service, list_args, calendar_list_entry, events, filter_func
            )
        return dict(items=sorted(events, key=_event_sort_key_function))
    except RefreshError as e:
        raise CredentialsError from e
    finally:
        # The client library automatically refreshes if it can, so update the creds.
        user_creds.update(credentials.__getstate__())


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


def _credentials_from_dict(creds_dict: dict) -> Credentials:
    return Credentials(
        token=creds_dict.get("_token"),
        refresh_token=creds_dict.get("_refresh_token"),
        id_token=creds_dict.get("_id_token"),
        token_uri=creds_dict.get("_token_uri"),
        client_id=creds_dict.get("_client_id"),
        client_secret=creds_dict.get("_client_secret"),
        scopes=creds_dict.get("_scopes"),
        quota_project_id=creds_dict.get("_quota_project_id"),
    )


def _add_calendar_events(service, list_args, calendar, events, filter_func):
    calendar_id = calendar["id"]
    try:
        events_result = (
            service.events()
            .list(calendarId=calendar_id, singleEvents=True, **list_args)
            .execute()
        )
    except HttpError as ex:
        _logger.error(
            'Error getting events from "%s". %s', calendar["summary"], ex,
        )
    else:
        events += [e for e in events_result.get("items", []) if filter_func(e)]


def _event_sort_key_function(event):
    start = event.get("start", {})
    # start may be specified by either 'date' or 'dateTime'
    return start.get("date", start.get("dateTime", ""))


class _DiscoveryCache:
    """Cache for Google service discovery.

    See https://github.com/googleapis/google-api-python-client/issues/325
    """

    def __init__(self) -> None:
        self._cache = {}

    def get(self, url):
        return self._cache.get(url)

    def set(self, url, content):
        self._cache[url] = content
