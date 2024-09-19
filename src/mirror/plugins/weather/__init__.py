"""Weather data backed by the Open Weather Map API and AirNow API.

https://openweathermap.org/api/one-call-api
https://docs.airnowapi.org/
"""

import logging
from asyncio import create_task, sleep
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_context import PluginContext

# database keys:
API_KEY = "api-key"
LOCATION = "location"
AIR_API_KEY = "air-api-key"
AIR_LOCATION = "air-location"

# Open Weather Map allows 1000 calls per day to their "One Call API". Leaving some room
# for development where we might be making double the number of requests for a while on
# some particular day, and since it seems plenty real-time we'll go with refreshing
# every 5 minutes (288 per day).
#
# AirNow typically updates observations once per hour, with a rate limit of 500 requests
# per hour.
REFRESH_INTERVAL = timedelta(minutes=5)

CONFIG_REFRESH_INTERVAL = timedelta(minutes=1)

WEATHER_URL = "https://api.openweathermap.org/data/3.0/onecall"
AIR_QUALITY_URL = "https://www.airnowapi.org/aq/observation/zipCode/current/"

_logger = logging.getLogger(__name__)
_state = {}


def configure_plugin(config_context: PluginConfigureContext) -> None:
    db = config_context.db
    print("Weather Plugin Set Up")
    db[API_KEY] = input("Open Weather Map API key: ").strip()
    db[LOCATION] = input("Weather location (lat,lon): ").strip()
    db[AIR_API_KEY] = input("AirNow API key: ").strip()
    db[AIR_LOCATION] = input("Zip Code: ").strip()
    # TODO: General config setting implementation?
    # TODO: Only require the user to enter the location once with conversion.


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
        weather_params = {
            "lat": lat,
            "lon": lon,
            "units": "imperial",
            "appid": key,
            "exclude": "hourly,minutely",
        }
        air_params = {
            "format": "application/json",
            "distance": 25,
            "zipCode": context.db[AIR_LOCATION],
            "API_KEY": context.db[AIR_API_KEY],
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                weather_response = await client.get(WEATHER_URL, params=weather_params)
                air_response = await client.get(AIR_QUALITY_URL, params=air_params)
            weather_response.raise_for_status()
            air_response.raise_for_status()
            data = _reshape(weather_response.json())
            data["air_quality"] = _reshape_air(air_response.json())
            await context.widget_updated(data)
            context.vote_connected()
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting weather data.")
        except Exception:
            _logger.exception("Error getting weather data.")
        await sleep(REFRESH_INTERVAL.total_seconds())


def _reshape(data: dict) -> dict:
    """Reshape the data from the API to be easier to work with."""
    tz = ZoneInfo(data["timezone"])
    return {
        "temp": data["current"]["temp"],
        "icon": _icon_class(
            data["current"]["weather"][0]["icon"],
            data["current"]["weather"][0]["id"],
        ),
        "summary": data["current"]["weather"][0]["description"],
        "feels": data["current"]["feels_like"],
        "wind": data["current"]["wind_speed"],
        "uvi": data["current"]["uvi"],
        "uviMax": data["daily"][0]["uvi"],
        "sunrise": _time_from_seconds(data["current"]["sunrise"], tz),
        "sunset": _time_from_seconds(data["current"]["sunset"], tz),
        "daily": _reshape_daily(data["daily"][:5], tz),
        "alerts": data.get("alerts", []),
    }


def _reshape_daily(daily: list[dict], tz: ZoneInfo) -> list[dict]:
    """Reshape the daily data from the API to be easier to work with."""
    return [
        {
            "day": (
                datetime.fromtimestamp(day["dt"]).astimezone(tz).strftime("%a")
                if i > 0
                else "Today"
            ),
            "icon": _icon_class(day["weather"][0]["icon"], day["weather"][0]["id"]),
            "temp_max": day["temp"]["max"],
            "temp_min": day["temp"]["min"],
            "precipitation": day["pop"] * 100,
        }
        for i, day in enumerate(daily)
    ]


def _icon_class(icon: str, id_: str) -> str:
    """Get the CSS class for the icon."""
    time = ""  # Neutral in terms of night/day by default.
    last_char = icon[-1]
    if last_char == "d":
        time = "day-"
    elif last_char == "n":
        time = "night-"
    return f"wi wi-owm-{time}{id_}"


def _time_from_seconds(seconds: int, tz: ZoneInfo) -> str:
    """Get a time string from seconds since epoch."""
    local = datetime.fromtimestamp(seconds, tz=UTC).astimezone(tz)
    return local.strftime("%I:%M %p")


def _reshape_air(data_list: list) -> dict:
    if not data_list:
        return {
            "aqi": -1,
            "category": "Unavailable",
        }
    data: dict = data_list[0]
    return {
        "aqi": data["AQI"],
        "category": data["Category"]["Name"],
    }
