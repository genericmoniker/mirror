# -*- coding: utf-8 -*-
import re
from trello import TrelloClient
from werkzeug.contrib.cache import SimpleCache

CACHE_TIMEOUT = 5 * 60

cache = SimpleCache()


def get_task_lists(config):
    """Get the current task lists."""
    data = cache.get('tasks')
    if data is None:
        data = get_task_lists_data(config)
        cache.set('tasks', data, CACHE_TIMEOUT)
    return data


def create_client(config):
    """Create a TrelloClient instance.

    Uses auth properties from instance/config.py.
    """
    return TrelloClient(
        api_key=config.get('TRELLO_API_KEY'),
        api_secret=config.get('TRELLO_API_SECRET'),
        token=config.get('TRELLO_TOKEN'),
        token_secret=config.get('TRELLO_TOKEN_SECRET'),
    )


def get_task_lists_data(config):
    """Get lists of tasks.

    :param config: application configuration.
    :return: a list of task list dicts.
    """
    client = create_client(config)
    task_lists = dict(items=[])
    board_re = re.compile(config.get('TRELLO_BOARD_RE').encode('UTF-8'))
    list_re = re.compile(config.get('TRELLO_LIST_RE').encode('UTF-8'))
    boards = client.list_boards()
    # noinspection PyTypeChecker
    for board in boards:
        if board_re.search(board.name):
            cards = board.get_cards()
            for list_ in board.get_lists(None):
                if list_re.search(list_.name):
                    task_lists['items'].append(list_dict(list_, cards))
    return task_lists


def list_dict(list_, cards):
    return dict(
        name=list_.name,
        tasks=[c.name for c in cards if c.list_id == list_.id]
    )
