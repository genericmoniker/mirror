# -*- coding: utf-8 -*-

"""Weather data backed by the Dark Sky Forecast API.

https://developer.forecast.io/docs/v2
"""

import requests
from werkzeug.contrib.cache import SimpleCache
from werkzeug.http import parse_cache_control_header
from werkzeug.datastructures import ResponseCacheControl

CACHE_MIN_SECONDS = 2 * 60

cache = SimpleCache()


def build_url(config):
    return 'https://api.forecast.io/forecast/{key}/{loc}'.format(
        key=config.get('FORECAST_API_KEY'),
        loc=config.get('FORECAST_LOCATION'),
        exclude='minutely,hourly',
    )


def get_cache_timeout(r):
    # Cache the weather data at a rate that the upstream service dictates, but
    # that also keeps us easily within the 1000 requests per day free limit.
    header = r.headers.get('Cache-Control')
    control = parse_cache_control_header(header, cls=ResponseCacheControl)
    try:
        return max(control.max_age, CACHE_MIN_SECONDS)
    except TypeError:
        return CACHE_MIN_SECONDS


def get_weather_data(config):
    data = cache.get('forecast')
    if data is None:
        r = requests.get(build_url(config))
        data = r.json()
        cache.set('forecast', data, get_cache_timeout(r))
    return data


def current_conditions(config):
    """Get the current weather conditions for the configured coordinates.

    :param config: Flask app config object.
    :return: dict of weather data.
    """
    data = get_weather_data(config)
    return data['currently']


def forecast(config):
    """Get the weather forecast for the configured coordinates.

    :param config: Flask app config object.
    :return: dict of weather data.
    """
    data = get_weather_data(config)
    return data['daily']
