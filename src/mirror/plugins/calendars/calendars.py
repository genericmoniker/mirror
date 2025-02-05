"""Calendars plugin."""

from asyncio import create_task
from typing import Any

from mirror.plugin_context import PluginContext

from . import agenda, coming_up, countdown
from .google_calendar import get_events

_state: dict[str, Any] = {"tasks": []}


def start_plugin(context: PluginContext) -> None:
    tasks = _state["tasks"]
    tasks.append(
        create_task(agenda.poll(context, get_events), name="agenda.refresh"),
    )
    tasks.append(
        create_task(coming_up.poll(context, get_events), name="coming_up.refresh"),
    )
    tasks.append(
        create_task(countdown.refresh(context, get_events), name="countdown.refresh"),
    )


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    for task in _state.get("tasks", []):
        if task:
            task.cancel()
