import asyncio
from contextlib import suppress
from datetime import timedelta
from pathlib import Path

import httpx

REFRESH_INTERVAL = timedelta(seconds=60)
OFFLINE_THRESHOLD = 30


_state = {}


def start_plugin(context):
    task = asyncio.create_task(_refresh(context), name="connectivity.refresh")
    _state["task"] = task


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context):
    disconnected_count = 0
    while True:
        data = {"error": None}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://api.ipify.org?format=json")
                response.raise_for_status()
                context.vote_connected()
                data = response.json()
                data.update({"connected": True, "error": None})
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

        await context.post_event("refresh", data)
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())
