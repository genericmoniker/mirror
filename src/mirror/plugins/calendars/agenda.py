"""Plugin module for getting events from the calendar agenda."""

import asyncio
import contextlib
import logging
import re
from collections.abc import Callable
from datetime import datetime, timedelta

from mirror.plugin_context import PluginContext

from . import common
from .datetime_utils import end_of_day_tz, now_tz

REFRESH_INTERVAL = timedelta(minutes=5)

_logger = logging.getLogger(__name__)


async def poll(
    context: PluginContext, get_events: Callable, wake_event: asyncio.Event
) -> None:
    while True:
        try:
            await refresh(context, get_events)
        except Exception:
            _logger.exception("Error getting agenda events.")
        wake_event.clear()
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(
                wake_event.wait(), timeout=REFRESH_INTERVAL.total_seconds()
            )


async def refresh(context: PluginContext, get_events: Callable) -> None:
    data = await common.refresh_data(
        context,
        get_events,
        common.range_to_list_args(_get_agenda_event_range),
    )
    if data.get("login_required"):
        widget_data = {
            "login_required": True,
            "auth_url": common.get_auth_url(context),
            "items": [],
        }
    else:
        widget_data = _reshape(data, context.config)
    await context.widget_updated(widget_data, "agenda")


def _get_agenda_event_range() -> tuple[str, str]:
    """Get times from now until the end of the day."""
    start = now_tz()
    stop = end_of_day_tz()
    _logger.info("agenda range: %s - %s", start.isoformat(), stop.isoformat())
    return start.isoformat(), stop.isoformat()


def _reshape(data: dict, config: dict) -> dict:
    """Reshape the data for the template."""
    return {
        "items": [_reshape_item(item, config) for item in data["items"]],
    }


def _reshape_item(item: dict, config: dict) -> dict:
    data = {}
    pattern = config.get(common.SUBORDINATE_FILTER)
    if pattern and re.match(pattern, item["calendar_id"]):
        data["subordinate"] = True
    else:
        data["subordinate"] = False

    if item["calendar_name"].lower() in ("dinner", "meals"):
        data["meals"] = True
    else:
        data["meals"] = False

    if "dateTime" not in item["start"]:
        return data | {
            "start": "All day - ",
            "summary": item["summary"],
            "current": False,
        }

    start_time = item["start"]["dateTime"]
    end_time = item["end"]["dateTime"]
    now = datetime.now().astimezone()
    return data | {
        "start": start_time.strftime("%-I:%M %p"),
        "summary": item["summary"],
        "current": start_time <= now <= end_time,
        "start_time": start_time,
        "end_time": end_time,
    }
