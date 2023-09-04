"""Net worth data of some number of financial accounts via Personal Capital.

WARNING: BROKEN AS OF NOV 2021.

See https://github.com/haochi/personalcapital/issues/20
"""
import logging
from asyncio import create_task, sleep
from datetime import timedelta

from mirror.plugin_context import PluginContext
from personalcapital.personalcapital import RequireTwoFactorException

from .worth import update_worth

REFRESH_INTERVAL = timedelta(hours=12)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context: PluginContext) -> None:
    task = create_task(_refresh(context), name="worth.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    """Get the net worth data."""
    while True:
        try:
            data = await update_worth(context.db, limit=10)
            await context.post_event("refresh", data)
        except RequireTwoFactorException:
            _logger.error("Please run `mirror-config --plugins=worth`")  # noqa: TRY400
        except Exception as ex:  # noqa: BLE001
            _logger.error("Error updating worth data: %s", ex)  # noqa: TRY400
        await sleep(REFRESH_INTERVAL.total_seconds())
