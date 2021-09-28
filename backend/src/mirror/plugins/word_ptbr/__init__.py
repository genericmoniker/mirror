"""Brazilian Portuguese Word-of-the-Day from transparent.com"""

import logging
import xml.etree.ElementTree as ET
from asyncio import create_task, sleep
from datetime import timedelta

import httpx

REFRESH_INTERVAL = timedelta(hours=8)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context):
    task = create_task(_refresh(context), name="word_ptbr.refresh")
    _state["task"] = task


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context):
    """Get the word of the day."""
    url = "https://wotd.transparent.com/rss/pt-widget.xml"
    while True:
        try:
            transport = httpx.AsyncHTTPTransport(retries=3)
            async with httpx.AsyncClient(transport=transport) as client:
                response = await client.get(url)
            response.raise_for_status()
            data = _parse(response.text)
            await context.post_event("refresh", data)
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Error getting word-of-the-day data.")

        await sleep(REFRESH_INTERVAL.total_seconds())


def _parse(xml):
    root = ET.fromstring(xml)
    return {
        "word": root.find("./words/word").text,
        "translation": root.find("./words/translation").text,
        "part_of_speech": root.find("./words/wordtype").text,
        "sentence": root.find("./words/fnphrase").text,
        "sentence_translation": root.find("./words/enphrase").text,
    }
