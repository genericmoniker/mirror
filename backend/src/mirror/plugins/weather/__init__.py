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

# Open Weather Map allows lots of calls (60/min) for free, but this seems sufficient.
REFRESH_INTERVAL = timedelta(minutes=2)

_loggger = logging.getLogger(__name__)
_state = {}


def configure_plugin(db):
    print("Weather Plugin Set Up")
    db[API_KEY] = input("Open Weather Map API key: ").strip()
    db[LOCATION] = input("Weather location (lat,lon): ").strip()
    # TODO: General config setting implementation?


def start_plugin(context):
    task = create_task(_refresh(context), name="weather.refresh")
    _state["task"] = task


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
        except httpx.RequestError:
            _loggger.exception("Error getting weather data.")
        # TODO: Cache the last data and only post an event if it changed. Or rather, do
        # that in the event bus.
        await sleep(REFRESH_INTERVAL.total_seconds())