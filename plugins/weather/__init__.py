"""Weather data backed by the Dark Sky Forecast API.

TODO: Darksky was acquired by Apple and the API will only work through the end of 2021.

https://darksky.net/dev/
"""
from datetime import timedelta

import requests
from flask import Blueprint, jsonify

# database keys:
API_KEY = "api-key"
LOCATION = "location"

CACHE_KEY = "weather data"

# For the "free" tier, we're limited to 1000 requests per day.
# A 2 minute refresh results in 60 * 24 / 2 = 720 requests.
REFRESH_INTERVAL = timedelta(minutes=2)


def configure_plugin(db):
    print("Weather Plugin Set Up")
    db[API_KEY] = input("Dark Sky API key: ").strip()
    db[LOCATION] = input("Weather location (lat,lon): ").strip()
    # TODO: General config setting implementation?


def create_plugin(context) -> Blueprint:
    context.cache.add_refresh(CACHE_KEY, REFRESH_INTERVAL, refresh_data)
    bp = Blueprint("weather", __name__, static_folder="static")

    @bp.route("/")
    def _get_weather_data():
        return jsonify(context.cache[CACHE_KEY])

    return bp


def get_scripts() -> list:
    return [
        ("weather.tag", "riot/tag"),
    ]


def refresh_data(db):
    """Get the weather data for the configured coordinates.

    :return: dict of weather data.
    """
    key = db.get(API_KEY)
    loc = db.get(LOCATION)
    url = f"https://api.darksky.net/forecast/{key}/{loc}"
    return requests.get(url, timeout=20).json()
