import asyncio
from contextlib import suppress
from datetime import timedelta
from pathlib import Path

import httpx

from mirror.plugin_context import PluginContext

REFRESH_INTERVAL = timedelta(seconds=60)
OFFLINE_THRESHOLD = 30


_state = {}


def start_plugin(context: PluginContext) -> None:
    task = asyncio.create_task(_refresh(context), name="connectivity.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    disconnected_count = 0
    while True:
        data = {"connected": True, "error": ""}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://api.ipify.org?format=json")
                response.raise_for_status()
                context.vote_connected()
                data = response.json()
        except httpx.RequestError as ex:
            context.vote_disconnected(ex)
            data.update({"error": str(ex) or repr(ex)})

        if context.is_connected:
            data.update({"connected": True})
            disconnected_count = 0
        else:
            data.update({"connected": False})
            disconnected_count += 1

        if disconnected_count == OFFLINE_THRESHOLD:
            # If we've been disconnected for a while, drop a file to the filesystem
            # to indicate that we are offline. A script outside the container can use
            # this to gracefully reboot.
            with suppress(IOError):
                Path("/home/appuser/instance/mirror-offline").touch(exist_ok=True)

        await context.widget_updated(data)
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())
