import asyncio
import logging
import re
from datetime import timedelta
from functools import partial

from . import common
from .datetime_utils import end_of_day_tz, parse_date_tz, start_of_day_tz

REFRESH_INTERVAL = timedelta(minutes=10)

_logger = logging.getLogger(__name__)


async def refresh(context):
    while True:
        try:
            data = await _refresh_data(context.db)
            await context.post_event("refresh_coming_up", data)
        except Exception:  # pylint:disable=broad-except
            _logger.exception("Error getting coming up events.")

        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())


async def _refresh_data(db):
    filter_pattern = db.get(common.COMING_UP_FILTER)
    filter_func = partial(_coming_up_filter, filter_pattern)
    list_args = common.range_to_list_args(_get_coming_up_event_range)
    return await common.refresh_data(db, list_args, filter_func)


def _get_coming_up_event_range():
    """Get times from tomorrow until a week from today."""
    start = start_of_day_tz() + timedelta(days=1)
    stop = end_of_day_tz() + timedelta(days=6)
    _logger.info("coming up range: %s - %s", start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()


def _coming_up_filter(pattern, event):
    # All day events only have a date, not a dateTime.
    if "dateTime" in event["start"]:
        return False
    # For multi-day events, skip them if they've already started.
    start = parse_date_tz(event["start"]["date"])
    if start <= start_of_day_tz():
        return False
    # Check any custom filters from the config.
    if pattern and re.match(pattern, event["summary"]):
        return False

    return True
