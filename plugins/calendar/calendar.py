from datetime import timedelta

from flask import Blueprint, jsonify

from . import agenda
from . import comingup


def create_plugin(context) -> Blueprint:
    context.cache.add_refresh(
        agenda.CACHE_KEY, agenda.REFRESH_INTERVAL, agenda.refresh_data
    )
    context.cache.add_refresh(
        comingup.CACHE_KEY, comingup.REFRESH_INTERVAL, comingup.refresh_data
    )

    bp = Blueprint("calendar", __name__, static_folder="static")

    @bp.route("/agenda")
    def _get_agenda_data():
        return jsonify(context.cache[agenda.CACHE_KEY])

    @bp.route("/comingup")
    def _get_comingup_data():
        return jsonify(context.cache[comingup.CACHE_KEY])

    return bp


def get_scripts() -> list:
    return [
        ("agenda.tag", "riot/tag"),
        ("comingup.tag", "riot/tag"),
        ("countdown.tag", "riot/tag"),
        ("countup.tag", "riot/tag"),
    ]
