"""School lunch menu."""
import asyncio
import logging
from datetime import timedelta

import httpx
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_context import PluginContext

# AirNow typically updates observations once per hour, with a rate limit of 500 requests
# per hour.
REFRESH_INTERVAL = timedelta(minutes=15)

URL = "https://www.airnowapi.org/aq/observation/zipCode/current/"

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context: PluginContext) -> None:
    task = asyncio.create_task(_refresh(context), name="air_quality.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


def configure_plugin(config_context: PluginConfigureContext) -> None:
    db = config_context.db
    print("Air Quality Plugin Set Up")
    db["api_key"] = input("AirNow API key: ").strip()
    db["zip_code"] = input("Zip Code: ").strip()


async def _refresh(context: PluginContext) -> None:
    while True:
        if "api_key" not in context.db or "zip_code" not in context.db:
            _logger.warning("Air quality plugin not configured.")
            await asyncio.sleep(REFRESH_INTERVAL.total_seconds())
            continue
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "format": "application/json",
                    "zipCode": context.db["zip_code"],
                    "distance": 25,
                    "API_KEY": context.db["api_key"],
                }
                response = await client.get(URL, params=params)
                response.raise_for_status()
                data = response.json()[0]
                await context.post_event("refresh", data)
                context.vote_connected()
        except httpx.TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error getting air quality.")
        except Exception:
            _logger.exception("Error getting air quality.")
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())
