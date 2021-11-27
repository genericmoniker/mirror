"""Weather data backed by the Open Weather Map API.

https://openweathermap.org/api/one-call-api
"""
import logging
from asyncio import create_task, sleep
from datetime import timedelta

import httpx

# database keys:
API_KEY = "api-key"
LOCATION = "location"

# Open Weather Map allows 1000 calls per day to their "One Call API". Leaving some room
# for development where we might be making double the number of requests for a while on
# some particular day, and since it seems plenty real-time we'll go with refreshing
# every 5 minutes (288 per day).
REFRESH_INTERVAL = timedelta(minutes=5)

_logger = logging.getLogger(__name__)
_state = {}


def configure_plugin(db):
    print("Weather Plugin Set Up")
    db[API_KEY] = input("Open Weather Map API key: ").strip()
    db[LOCATION] = input("Weather location (lat,lon): ").strip()
    # TODO: General config setting implementation?


def start_plugin(context):
    task = create_task(_refresh(context), name="weather.refresh")
    _state["task"] = task


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context):
    """Get the weather data for the configured coordinates.

    :return: dict of weather data.
    """
    key = context.db.get(API_KEY)
    loc = context.db.get(LOCATION)
    lat, lon = loc.split(",")
    params = {
        "lat": lat,
        "lon": lon,
        "units": "imperial",
        "appid": key,
        "exclude": "hourly,minutely",
    }
    while True:
        try:
            async with httpx.AsyncClient() as client:
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
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Error getting weather data.")
        await sleep(REFRESH_INTERVAL.total_seconds())
