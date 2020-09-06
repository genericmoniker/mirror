import logging
from datetime import timedelta

from . import common
from .datetimeutils import end_of_day_tz

CACHE_KEY = "countdown data"
REFRESH_INTERVAL = timedelta(minutes=20)

_logger = logging.getLogger(__name__)


def refresh_data(db):
    """Get events tagged in the calendar for long-term countdowns.

    This includes future events with "mirror-countdown" in them.
    """
    start = (end_of_day_tz() + timedelta(days=7)).isoformat()
    query = "mirror-countdown"
    list_args = {"timeMin": start, "q": query}
    _logger.info("countdown start: %s", start)
    return common.refresh_data(db, list_args)
