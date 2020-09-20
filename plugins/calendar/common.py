import logging

from .google_calendar import CredentialsError, get_calendar_events

_logger = logging.getLogger(__name__)

# database keys:
CLIENT_CREDENTIALS = "client-creds"
USER_CREDENTIALS = "user-creds"
COMING_UP_FILTER = "coming-up-filter"


def range_to_list_args(event_range_func):
    start, stop = event_range_func()
    return {"timeMin": start, "timeMax": stop}


def refresh_data(db, list_args, filter_func=None):
    try:
        user_creds = db.get(USER_CREDENTIALS)
        events = get_calendar_events(user_creds, list_args, filter_func)

        # Save potentially refreshed creds.
        db[USER_CREDENTIALS] = user_creds

        return events

    except CredentialsError as e:
        _logger.error("Please run `python configure.py --plugin=calendar` (%s)", e)