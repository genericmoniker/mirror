"""Net worth data of some number of financial accounts via Personal Capital."""
import logging
from asyncio import create_task, sleep
from datetime import timedelta

from personalcapital.personalcapital import RequireTwoFactorException

from .configure import configure_plugin
from .worth import update_worth

REFRESH_INTERVAL = timedelta(hours=12)

_logger = logging.getLogger(__name__)
_state = {}


def start_plugin(context):
    task = create_task(_refresh(context), name="worth.refresh")
    _state["task"] = task


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context):
    """Get the net worth data."""
    while True:
        try:
            data = await update_worth(context.db, limit=10)
            await context.post_event("refresh", data)
        except RequireTwoFactorException:
            _logger.error("Please run `mirror-config --plugins=worth`")
        except Exception as ex:  # pylint: disable=broad-except
            _logger.error("Error updating worth data: %s", ex)
        await sleep(REFRESH_INTERVAL.total_seconds())
