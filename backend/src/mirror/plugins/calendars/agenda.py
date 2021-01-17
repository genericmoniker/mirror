import asyncio
import logging
from datetime import timedelta

from . import common
from .datetime_utils import end_of_day_tz, now_tz

REFRESH_INTERVAL = timedelta(minutes=5)

_logger = logging.getLogger(__name__)


async def refresh(context):
    while True:
        try:
            data = await _refresh_data(context.db)
            await context.post_event("refresh_agenda", data)
        except Exception:  # pylint:disable=broad-except
            _logger.exception("Error getting agenda events.")

        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())


async def _refresh_data(db):
    return await common.refresh_data(
        db, common.range_to_list_args(_get_agenda_event_range)
    )


def _get_agenda_event_range():
    """Get times from now until the end of the day."""
    start = now_tz()
    stop = end_of_day_tz()
    _logger.info("agenda range: %s - %s", start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()
