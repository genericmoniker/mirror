# -*- coding: utf-8 -*-
from flask import Flask, jsonify, render_template

import weather

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/alive')
def alive():
    return 'OK'


@app.route('/weather')
def current_weather():
    return jsonify(weather.current_conditions(app.config))


@app.route('/forecast')
def forecast():
    return jsonify(weather.forecast(app.config))


if __name__ == '__main__':
    app.run()
