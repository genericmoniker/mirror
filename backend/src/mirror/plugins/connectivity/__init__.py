import asyncio
from datetime import timedelta

import httpx

REFRESH_INTERVAL = timedelta(seconds=60)


_state = {}


def start_plugin(context):
    task = asyncio.create_task(_refresh(context), name="connectivity.refresh")
    _state["task"] = task


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context):
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://api.ipify.org?format=json")
                response.raise_for_status()
                data = response.json()
                data.update({"connected": True, "error": None})
        except httpx.RequestError as ex:
            error_message = str(ex) or repr(ex)
            data = {"connected": False, "error": error_message}
        await context.post_event("refresh", data)
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())
