"""Net worth data of some number of financial accounts via Personal Capital."""
from datetime import timedelta

from flask import Blueprint, jsonify

from .configure import configure_plugin
from .worth import update_worth

CACHE_KEY = "worth data"

REFRESH_INTERVAL = timedelta(hours=12)


def create_plugin(context) -> Blueprint:
    context.cache.add_refresh(CACHE_KEY, REFRESH_INTERVAL, refresh_data)
    bp = Blueprint("worth", __name__, static_folder="static")

    @bp.route("/")
    def _get_worth_data():
        return jsonify(context.cache[CACHE_KEY])

    return bp


def get_scripts() -> list:
    return [
        ("worth.tag", "riot/tag"),
        ("Chart.min.js", "application/javascript"),
    ]


def refresh_data(db):
    """Get the net worth data."""
    return update_worth(db, limit=10)
