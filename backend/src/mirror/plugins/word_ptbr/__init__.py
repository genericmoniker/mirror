"""Brazilian Portuguese Word-of-the-Day from transparent.com."""

import logging
from asyncio import create_task, sleep
from datetime import timedelta

import httpx
from defusedxml import ElementTree
from mirror.plugin_context import PluginContext

REFRESH_INTERVAL = timedelta(hours=8)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context: PluginContext) -> None:
    task = create_task(_refresh(context), name="word_ptbr.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    """Get the word of the day."""
    url = "https://wotd.transparent.com/rss/pt-widget.xml"
    while True:
        try:
            transport = httpx.AsyncHTTPTransport(retries=3)
            async with httpx.AsyncClient(transport=transport, timeout=10) as client:
                response = await client.get(url)
            response.raise_for_status()
            data = _parse(response.text)
            await context.post_event("refresh", data)
            context.vote_connected()
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting word-of-the-day data.")
        except Exception:
            _logger.exception("Error getting word-of-the-day data.")

        await sleep(REFRESH_INTERVAL.total_seconds())


def _parse(xml: str) -> dict:
    root = ElementTree.fromstring(xml)
    return {
        "word": root.find("./words/word").text,
        "translation": root.find("./words/translation").text,
        "part_of_speech": root.find("./words/wordtype").text,
        "sentence": root.find("./words/fnphrase").text,
        "sentence_translation": root.find("./words/enphrase").text,
    }
