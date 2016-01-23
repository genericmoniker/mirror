# -*- coding: utf-8 -*-
import requests

_ROOT = 'http://api.openweathermap.org/data/2.5'


def current_conditions(config):
    """Get the current weather conditions for the configured city.

    :param config: Flask app config object.
    :return: dict of weather data.
    """
    api_key = config.get('OPENWEATHERMAP_API_KEY')
    city_id = config.get('WEATHER_CITY_ID')
    units = config.get('WEATHER_UNITS', 'imperial')
    url = '{}/weather?id={}&appid={}&units={}'.format(
        _ROOT,
        city_id,
        api_key,
        units,
    )
    r = requests.get(url)
    json = r.json()
    return dict(
        location=json.get('name'),
        temp=round(json.get('main', {}).get('temp')),
        temp_max=round(json.get('main', {}).get('temp_max')),
        temp_min=round(json.get('main', {}).get('temp_min')),
        icon_class='wi wi-owm-' + str(json.get('weather', [])[0].get('id')),
        main=json.get('weather', [])[0].get('main'),
        sunrise=json.get('sys', {}).get('sunrise'),
        sunset=json.get('sys', {}).get('sunset'),
    )


def forecast(config):
    """Get the weather forecast for the configured city.

    :param config: Flask app config object.
    :return: dict of weather data.
    """
    api_key = config.get('OPENWEATHERMAP_API_KEY')
    city_id = config.get('WEATHER_CITY_ID')
    units = config.get('WEATHER_UNITS', 'imperial')
    url = '{}/forecast?id={}&appid={}&units={}'.format(
        _ROOT,
        city_id,
        api_key,
        units,
    )
    r = requests.get(url)
    json = r.json()
    return dict()  # todo
