"""Jokes from jokeapi.dev."""

import logging
from asyncio import create_task, sleep
from datetime import timedelta

import httpx
from mirror.plugin_context import PluginContext

REFRESH_INTERVAL = timedelta(hours=1)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context: PluginContext) -> None:
    task = create_task(_refresh(context), name="joke.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    """Get a joke."""
    url = "https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,explicit"
    while True:
        try:
            transport = httpx.AsyncHTTPTransport(retries=3)
            async with httpx.AsyncClient(transport=transport, timeout=10) as client:
                response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            await context.widget_updated(data)
            context.vote_connected()
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting joke data.")
        except Exception:
            _logger.exception("Error getting joke data.")

        await sleep(REFRESH_INTERVAL.total_seconds())
