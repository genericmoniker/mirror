"""Weather data backed by the Open Weather Map API.

https://openweathermap.org/api/one-call-api
"""
import logging
from asyncio import create_task, sleep
from datetime import timedelta

import httpx
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_context import PluginContext

# database keys:
API_KEY = "api-key"
LOCATION = "location"

# Open Weather Map allows 1000 calls per day to their "One Call API". Leaving some room
# for development where we might be making double the number of requests for a while on
# some particular day, and since it seems plenty real-time we'll go with refreshing
# every 5 minutes (288 per day).
REFRESH_INTERVAL = timedelta(minutes=5)

CONFIG_REFRESH_INTERVAL = timedelta(minutes=1)

_logger = logging.getLogger(__name__)
_state = {}


def configure_plugin(config_context: PluginConfigureContext) -> None:
    db = config_context.db
    print("Weather Plugin Set Up")
    db[API_KEY] = input("Open Weather Map API key: ").strip()
    db[LOCATION] = input("Weather location (lat,lon): ").strip()
    # TODO: General config setting implementation?


def start_plugin(context: PluginContext) -> None:
    task = create_task(_refresh(context), name="weather.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    """Get the weather data for the configured coordinates.

    :return: dict of weather data.
    """
    while True:
        key = context.db.get(API_KEY)
        loc = context.db.get(LOCATION)
        if not key or not loc:
            _logger.warning("Weather plugin not configured.")
            await sleep(CONFIG_REFRESH_INTERVAL.total_seconds())
            continue

        lat, lon = loc.split(",")
        params = {
            "lat": lat,
            "lon": lon,
            "units": "imperial",
            "appid": key,
            "exclude": "hourly,minutely",
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                url = "https://api.openweathermap.org/data/2.5/onecall"
                response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            await context.post_event("refresh", data)
            context.vote_connected()
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting weather data.")
        except Exception:
            _logger.exception("Error getting weather data.")
        await sleep(REFRESH_INTERVAL.total_seconds())
