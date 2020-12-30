import asyncio
import logging
from datetime import timedelta

from . import common
from .datetime_utils import end_of_day_tz

REFRESH_INTERVAL = timedelta(minutes=20)

_logger = logging.getLogger(__name__)


async def refresh(context):
    while True:
        data = await _refresh_data(context.db)
        await context.post_event("refresh_countdown", data)
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())


async def _refresh_data(db):
    """Get events tagged in the calendar for long-term countdowns.

    This includes future events with "mirror-countdown" in them.
    """
    start = (end_of_day_tz() + timedelta(days=7)).isoformat()
    query = "mirror-countdown"
    list_args = {"timeMin": start, "q": query}
    _logger.info("countdown start: %s", start)
    return common.refresh_data(db, list_args)
