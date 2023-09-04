"""School lunch menu."""
import asyncio
import logging
from datetime import datetime, timedelta

import httpx
from mirror.plugin_context import PluginContext

REFRESH_INTERVAL = timedelta(hours=8)

# TODO: Make this configurable...
URL_TEMPLATE = (
    "https://alpineschools.nutrislice.com/menu/api/weeks/school"
    "/skyridge-high-school/menu-type/lunch/{year}/{month:02}/{day:02}/?format=json"
)


_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context: PluginContext) -> None:
    task = asyncio.create_task(_refresh(context), name="menu.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(_build_url())
                response.raise_for_status()
                full_data = response.json()
                data = _reshape_full_data(full_data)
                await context.post_event("refresh", data)
                context.vote_connected()
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting menu.")
        except Exception:
            _logger.exception("Error getting menu.")
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())


def _build_url() -> str:
    # This URL returns the week containing the specified date, not 7 days starting
    # from the specified date.
    today = datetime.now()  # noqa: DTZ005
    return URL_TEMPLATE.format(year=today.year, month=today.month, day=today.day)


def _reshape_full_data(full_data: dict) -> dict:
    """Reshape full data into simple keys/values.

    Output example:

    {
        "2021-08-16": None,
        "2021-08-17": "Chicken Teriyaki",
        "2021-08-18": "Taco Soup",
    }

    """
    data = {}
    for day in full_data.get("days", []):
        key = day["date"]
        try:
            value = day["menu_items"][0]["food"]["name"]
        except (IndexError, KeyError, TypeError):
            value = None

        data[key] = value
    return data
