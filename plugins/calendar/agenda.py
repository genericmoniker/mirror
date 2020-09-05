from datetime import timedelta

import logging

from .datetimeutils import end_of_day_tz, now_tz
from .google_calendar import CredentialsError, get_calendar_events

CACHE_KEY = "agenda data"
REFRESH_INTERVAL = timedelta(minutes=5)

_logger = logging.getLogger(__name__)


def refresh_data(db):
    try:
        user_creds = db.get("user-creds")
        start, stop = get_agenda_event_range()
        list_args = {"timeMin": start, "timeMax": stop}
        events = get_calendar_events(user_creds, list_args)

        # Save potentially refreshed creds.
        db["user-creds"] = user_creds

        return events

    except CredentialsError as e:
        _logger.error("Please run `python configure.py --plugin=calendar` (%s)", e)


def get_agenda_event_range():
    """Get times from now until the end of the day."""
    start = now_tz()
    stop = end_of_day_tz()
    _logger.info("agenda range: %s - %s", start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()
