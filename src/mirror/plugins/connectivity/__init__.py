from datetime import timedelta
import aiohttp
from aiohttp.client_exceptions import ClientError

REFRESH_INTERVAL = timedelta(minutes=1)


def start_plugin(context):
    context.create_periodic_task(refresh, REFRESH_INTERVAL)


async def refresh(context):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.ipify.org?format=json") as response:
                response.raise_for_status()
                data = await response.json()
                data.update({"connected": True, "error": None})
    except ClientError as ex:
        data = {"connected": False, "error": str(ex)}
    await context.post_event("refresh", data)
