import logging
from asyncio import create_task
from io import StringIO
from typing import *  # pylint: disable=wildcard-import,unused-wildcard-import

from . import agenda, coming_up, countdown

_logger = logging.getLogger(__name__)
_state: Dict[str, Any] = {"tasks": []}


def start_plugin(context):
    tasks = _state["tasks"]
    tasks.append(create_task(agenda.refresh(context), name="agenda.refresh"))
    tasks.append(create_task(coming_up.refresh(context), name="coming_up.refresh"))
    tasks.append(create_task(countdown.refresh(context), name="countdown.refresh"))


def stop_plugin(context):  # pylint: disable=unused-argument
    for task in _state.get("tasks"):
        if task:
            task.cancel()


def dump_tasks(context):  # pylint: disable=unused-argument
    file = StringIO()
    print("Dumping calendars tasks", file=file)
    for task in _state.get("tasks"):
        task.print_stack(file=file)
    _logger.info(file.getvalue())
