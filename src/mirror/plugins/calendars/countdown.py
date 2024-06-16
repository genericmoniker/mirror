"""Module for countdown to a calendar event."""
import asyncio
import logging
from collections.abc import Callable
from datetime import timedelta

from mirror.plugin_context import PluginContext

from . import common
from .datetime_utils import end_of_day_tz, parse_date_tz, relative_time

REFRESH_INTERVAL = timedelta(minutes=20)

_logger = logging.getLogger(__name__)


async def refresh(context: PluginContext, get_events: Callable) -> None:
    while True:
        try:
            data = await _refresh_data(context.db, get_events)
            if data:
                await context.widget_updated(_reshape(data), "countdown")
        except Exception:
            _logger.exception("Error getting countdown events.")

        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())


async def _refresh_data(db: dict, get_events: Callable) -> dict | None:
    """Get events tagged in the calendar for long-term countdowns.

    This includes future events with "mirror-countdown" in them.
    """
    start = (end_of_day_tz() + timedelta(days=7)).isoformat()
    query = "mirror-countdown"
    list_args = {"timeMin": start, "q": query}
    _logger.info("countdown start: %s", start)
    return await common.refresh_data(db, get_events, list_args)


def _reshape(data: dict) -> dict:
    """Reshape the data to be more useful for the widget."""
    return {
        "items": [
            {
                "summary": event["summary"],
                "date": (start := parse_date_tz(event["start"]["date"])),
                "relative": relative_time(start),
                "days_from_now": (start - end_of_day_tz()).days,
            }
            for event in data["items"]
        ],
    }
