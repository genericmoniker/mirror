"""Internet connectivity monitoring plugin."""
from datetime import timedelta
from flask import Blueprint, jsonify
import requests
from requests.exceptions import RequestException

CACHE_KEY = "connectivity data"

REFRESH_INTERVAL = timedelta(minutes=1)


def configure_plugin(db):
    pass


def create_plugin(context) -> Blueprint:
    context.cache.add_refresh(CACHE_KEY, REFRESH_INTERVAL, refresh_data)
    bp = Blueprint("connectivity", __name__, static_folder="static")

    @bp.route("/")
    def _get_connectivity_data():
        return jsonify(context.cache[CACHE_KEY])

    return bp


def get_scripts() -> list:
    return [
        ("connectivity.tag", "riot/tag"),
    ]


def refresh_data(db):
    """Get the connectivity data.

    :return: dict of connectivity data.
    """
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=10)
        response.raise_for_status()
        data = response.json()
        data.update({"connected": True, "error": None})
        return data
    except RequestException as e:
        return {"connected": False, "error": str(e)}
