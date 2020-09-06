import logging
from datetime import timedelta

from . import common
from .datetimeutils import end_of_day_tz, now_tz

CACHE_KEY = "agenda data"
REFRESH_INTERVAL = timedelta(minutes=5)

_logger = logging.getLogger(__name__)


def refresh_data(db):
    return common.refresh_data(db, get_agenda_event_range)


def get_agenda_event_range():
    """Get times from now until the end of the day."""
    start = now_tz()
    stop = end_of_day_tz()
    _logger.info("agenda range: %s - %s", start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()
