from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template
from pathlib import Path

from flask import request
from raven.contrib.flask import Sentry

import agenda
import messages
import tasks
import weather
from log import setup_logging

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')
setup_logging(app.config.get('LOG_FILE_PATH'))
if 'SENTRY_CONFIG' in app.config.keys():
    sentry = Sentry(app)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/rotate_count')
def rotate_page_count():
    path = Path(app.root_path, app.template_folder)
    pages = list(path.glob('rotate_*.html'))
    return jsonify({
        'count': len(pages)
    })


@app.route('/rotate')
def rotate_page():
    counter = int(request.args.get('counter'))
    path = Path(app.root_path, app.template_folder)
    pages = list(path.glob('rotate_*.html'))
    template = pages[counter % len(pages)]
    relative = str(template.relative_to(path))
    return render_template(relative)


@app.route('/alive')
def alive():
    return 'OK'


@app.route('/weather')
def current_weather():
    return jsonify(weather.current_conditions())


@app.route('/forecast')
def forecast():
    return jsonify(weather.forecast())


@app.route('/weather_alerts')
def weather_alerts():
    return jsonify(weather.alerts())


@app.route('/agenda')
def upcoming_agenda():
    return jsonify(agenda.get_agenda())


@app.route('/coming-up')
def upcoming_all_day_events():
    return jsonify(agenda.get_coming_up())


@app.route('/tasks')
def task_lists():
    return jsonify(tasks.get_task_lists(app.config))


@app.route('/message')
def message():
    return messages.get_message()


if __name__ == '__main__':
    sched = BackgroundScheduler()
    agenda.init_cache(app.config, sched)
    weather.init_cache(app.config, sched)
    sched.start()
    app.run(debug=False)
