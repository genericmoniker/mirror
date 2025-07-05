"""Plugin to display sleep data from ResMed myAir.

I was planning to use the myair_py library, which is a "soft fork" of a Home Assistant
plugin. Authentication didn't seem to work. The original plugin has been updated
significantly since the fork, but isn't a stand-alone library.

Fork: https://github.com/silverman63/myair-py Original:
https://github.com/prestomation/resmed_myair_sensors
"""

import logging
from asyncio import Task, create_task
from asyncio import sleep as async_sleep
from datetime import timedelta
from getpass import getpass

from aiohttp import ClientConnectionError, ClientSession
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_context import PluginContext
from myair_py.myair_client import MyAirConfig
from myair_py.new_client import RESTClient

REFRESH_INTERVAL = timedelta(hours=1)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context: PluginContext) -> None:
    if context.db.get("username"):
        task = create_task(_refresh(context), name="sleep.refresh")
        task.add_done_callback(_task_done)
        _state["task"] = task
    else:
        _logger.info("Plugin not configured.")


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.remove_done_callback(_task_done)
        task.cancel()


def _task_done(task: Task) -> None:
    _logger.warning("Sleep task unexpectedly done: %s", task.exception())


def configure_plugin(config_context: PluginConfigureContext) -> None:
    db = config_context.db
    print("Sleep Plugin Set Up")
    db["username"] = input("MyAir username: ").strip()
    db["password"] = getpass("MyAir password: ").strip()


async def _refresh(context: PluginContext) -> None:
    config = MyAirConfig(context.db["username"], context.db["password"], "NA")
    session = ClientSession()
    client = RESTClient(config, session)
    while True:
        try:
            await client.connect()
            data = await client.get_sleep_records()
            await context.widget_updated(data)
            context.vote_connected()
        except ClientConnectionError as ex:
            context.vote_disconnected(ex)
            _logger.exception("Network error getting sleep data.")
        except Exception:
            _logger.exception("Error getting sleep data.")
        await async_sleep(REFRESH_INTERVAL.total_seconds())
