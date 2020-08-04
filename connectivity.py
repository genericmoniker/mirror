import requests
from requests.exceptions import RequestException

from cache import Cache

REFRESH_MINUTES = 1

cache = None


def init_cache(config, scheduler):
    """Initialize the connectivity data cache.

    :param config: Flask app config object.
    :param scheduler: Scheduler to periodically update the data.
    """
    global cache
    cache = Cache(
        scheduler,
        'Refresh Internet Connectivity',
        REFRESH_MINUTES,
        check_connectivity
    )


def check_connectivity():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=10)
        response.raise_for_status()
        data = response.json()
        data.update({'connected': True, 'error': None})
        return data
    except RequestException as e:
        return {'connected': False, 'error': str(e)}


def get_connectivity():
    """Get the connectivity data for the server.

    :return: dict of connectivity data.
    """
    assert cache, 'init_cache must be called first!'
    return cache.get()
