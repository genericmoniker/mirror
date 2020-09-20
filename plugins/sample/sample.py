"""Server-side implementation of the plugin.

Typically, the server-side gets the data and puts it into a form that is easy for the
client-side tag to display.
"""
from datetime import timedelta
from random import choice

from flask import Blueprint, jsonify

CACHE_KEY = "sample data"
REFRESH_INTERVAL = timedelta(minutes=5)


def create_plugin(context) -> Blueprint:
    """Create the plugin's HTTP endpoints.

    The full plugin context is provided to enable caching and reading/writing data from
    the database.
    """

    # Use the context cache to automatically update plugin data.
    context.cache.add_refresh(CACHE_KEY, REFRESH_INTERVAL, refresh_data)

    # The plugin creates a Flask blueprint with as many routes as it wants.
    bp = Blueprint("sample", __name__, static_folder="static")

    @bp.route("/")
    def _get_sample_data():
        return jsonify(context.cache[CACHE_KEY])

    return bp


def get_scripts() -> list:
    """Get a list of scripts this plugin uses.

    Usually a plugin provides at least one Riot.js tag as a script.

    The scripts are a tuple of (filename, type). The filename is relative to the
    bluprint "static" folder.
    """
    return [("sample.tag", "riot/tag")]


def refresh_data(db):
    """Refresh the plugin's data.

    Cache refresh functions are given the context db so that they can reference
    configuration data stored there, such as API secrets, settings, etc.
    """
    return {
        "greeting": choice(["Hi", "Hello", "Hey there"]),
        "recipient": db.get("recipient", "world"),
    }
