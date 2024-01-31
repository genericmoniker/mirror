"""Plugin module for getting upcoming events."""
import asyncio
import logging
import re
from datetime import timedelta
from functools import partial

from mirror.plugin_context import PluginContext

from . import common
from .datetime_utils import (
    end_of_day_tz,
    parse_date_tz,
    short_relative_time,
    start_of_day_tz,
)

REFRESH_INTERVAL = timedelta(minutes=10)

_logger = logging.getLogger(__name__)


async def refresh(context: PluginContext) -> None:
    while True:
        try:
            data = await _refresh_data(context.db)
            if data:
                await context.widget_updated(_reshape(data), "coming_up")
        except Exception:
            _logger.exception("Error getting coming up events.")

        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())


async def _refresh_data(db: dict) -> dict | None:
    filter_pattern = db.get(common.COMING_UP_FILTER)
    filter_func = partial(_coming_up_filter, filter_pattern)
    list_args = common.range_to_list_args(_get_coming_up_event_range)
    return await common.refresh_data(db, list_args, filter_func)


def _get_coming_up_event_range() -> tuple[str, str]:
    """Get times from tomorrow until a week from today."""
    start = start_of_day_tz() + timedelta(days=1)
    stop = end_of_day_tz() + timedelta(days=6)
    _logger.info("coming up range: %s - %s", start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()


def _coming_up_filter(pattern: str, event: dict) -> bool:
    # We mainly want all day events. All day events only have a date, not a dateTime.
    # But include events anyway if they are count-down events.
    is_all_day = "dateTime" not in event["start"]
    is_countdown = "mirror-countdown" in event.get("description", "").lower()
    if not is_all_day and not is_countdown:
        return False
    # For multi-day events, skip them if they've already started.
    if is_all_day:
        start = parse_date_tz(event["start"]["date"])
        if start <= start_of_day_tz():
            return False
    # Check any custom filters from the config.
    if pattern and re.match(pattern, event["summary"]):
        return False

    return True


def _reshape(data: dict) -> dict:
    """Reshape the data for the template."""
    return {
        "items": [_reshape_item(item) for item in data["items"]],
    }


def _reshape_item(item: dict) -> dict:
    start = item["start"]
    start_time = parse_date_tz(start.get("dateTime", start["date"]))
    return {
        "summary": item["summary"],
        "relative": short_relative_time(start_time),
    }
