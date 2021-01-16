import asyncio
from datetime import timedelta

import httpx

REFRESH_INTERVAL = timedelta(seconds=20)


_state = {}


def start_plugin(context):
    task = asyncio.create_task(_refresh(context), name="connectivity.refresh")
    _state["task"] = task


# TODO: implement calls to stop_plugin in main.py
def stop_plugin(context):
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
            data = {"connected": False, "error": str(ex)}
        # TODO: Cache the last data and only post an event if it changed.
        await context.post_event("refresh", data)
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())
