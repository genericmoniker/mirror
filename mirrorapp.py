import sys
from pathlib import Path

import connectivity
import database
import weather
import worth
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template, request
from raven.contrib.flask import Sentry

import agenda
import messages
from log import setup_logging

app = Flask(__name__, instance_relative_config=True)
app.config.from_object("config")
app.config.from_pyfile("config.py")
setup_logging()
if "SENTRY_CONFIG" in app.config.keys():
    sentry = Sentry(app)


@app.route("/")
def root():
    return render_template("index.html")


@app.route("/rotate_count")
def rotate_page_count():
    path = Path(app.root_path, app.template_folder)
    pages = list(path.glob("rotate_*.html"))
    return jsonify({"count": len(pages)})


@app.route("/rotate")
def rotate_page():
    counter = int(request.args.get("counter"))
    path = Path(app.root_path, app.template_folder)
    pages = list(path.glob("rotate_*.html"))
    template = pages[counter % len(pages)]
    relative = str(template.relative_to(path))
    return render_template(relative)


@app.route("/alive")
def alive():
    return "OK"


@app.route("/connectivity")
def get_connectivity():
    return jsonify(connectivity.get_connectivity())


@app.route("/weather")
def current_weather():
    return jsonify(weather.get_weather())


@app.route("/worth")
def current_worth():
    limit = int(request.args.get("limit", 30))
    return jsonify(worth.get_worth(limit))


@app.route("/agenda")
def upcoming_agenda():
    return jsonify(agenda.get_agenda())


@app.route("/coming-up")
def upcoming_all_day_events():
    return jsonify(agenda.get_coming_up())


@app.route("/countdown")
def countdown_events():
    return jsonify(agenda.get_countdown())


@app.route("/message")
def message():
    return messages.get_message()


@app.before_first_request
def startup():
    database.init()
    scheduler = BackgroundScheduler()
    agenda.init_cache(app.config, scheduler)
    connectivity.init_cache(app.config, scheduler)
    messages.init_cache(app, scheduler)
    weather.init_cache(app.config, scheduler)
    worth.init(scheduler)
    scheduler.start()


def setup_application():
    database.init()
    database.db.connect()
    try:
        worth.setup()
    finally:
        database.db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_application()
    else:
        app.run(debug=False)
