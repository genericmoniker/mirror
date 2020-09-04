from datetime import timedelta

from flask import Blueprint, jsonify

import agenda

AGENDA_CACHE_KEY = "agenda data"
AGENDA_REFRESH_INTERVAL = timedelta(minutes=5)


def create_plugin(context) -> Blueprint:
    context.cache.add_refresh(
        AGENDA_CACHE_KEY, AGENDA_REFRESH_INTERVAL, agenda.refresh_data
    )

    bp = Blueprint("calendar", __name__, static_folder="static")

    @bp.route("/agenda")
    def _get_agenda_data():
        return jsonify(context.cache[AGENDA_CACHE_KEY])

    return bp


def get_scripts() -> list:
    return [
        ("agenda.tag", "riot/tag"),
        ("comingup.tag", "riot/tag"),
        ("countdown.tag", "riot/tag"),
        ("countup.tag", "riot/tag"),
    ]
