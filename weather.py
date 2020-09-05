"""Weather data backed by the Dark Sky Forecast API.

https://darksky.net/dev/
"""
from functools import partial

import requests

from cache import Cache

# For the "free" tier, we're limited to 1000 requests per day.
# A 2 minute refresh results in 60 * 24 / 2 = 720 requests.
REFRESH_MINUTES = 2

cache = None


def init_cache(config, scheduler):
    """Initialize the weather data cache.

    :param config: Flask app config object.
    :param scheduler: Scheduler to periodically update the data.
    """
    global cache
    cache = Cache(
        scheduler,
        "Refresh Weather",
        REFRESH_MINUTES,
        partial(get_weather_data, build_url(config)),
    )


def build_url(config):
    return "https://api.darksky.net/forecast/{key}/{loc}".format(
        key=config.get("FORECAST_API_KEY"),
        loc=config.get("FORECAST_LOCATION"),
        exclude="minutely,hourly",
    )


def get_weather_data(url):
    return requests.get(url, timeout=20).json()


def get_weather():
    """Get the weather data for the configured coordinates.

    :return: dict of weather data.
    """
    assert cache, "init_cache must be called first!"
    return cache.get()
