from asyncio import create_task
from typing import *  # pylint: disable=wildcard-import,unused-wildcard-import

from . import agenda, coming_up, countdown

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
