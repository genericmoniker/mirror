"""Step count from the Fitbit API."""
import logging
from asyncio import create_task, sleep
from datetime import datetime, timedelta

from .fitbit import CredentialsError, get_activity

# A forum post said that devices tend to sync every 15 minutes when in range of a phone.
REFRESH_INTERVAL = timedelta(minutes=15)

# database keys:
CLIENT_ID = "client_id"
CLIENT_SECRET = "client_secret"
AUTHORIZATION_CODE = "authorization_code"
ACCESS_TOKEN = "access_token"
REFRESH_TOKEN = "refresh_token"

_logger = logging.getLogger(__name__)
_state = {}


def configure_plugin(db):
    print("Activity Plugin Set Up")
    db[CLIENT_ID] = input("Fitbit client ID (from app registration): ").strip()
    db[CLIENT_SECRET] = input("Fitbit client secret (from app registration): ").strip()
    db[AUTHORIZATION_CODE] = input("Authorization code (from user grant): ").strip()
    db[ACCESS_TOKEN] = None
    db[REFRESH_TOKEN] = None


def start_plugin(context):
    task = create_task(_refresh(context), name="activity.refresh")
    _state["task"] = task


async def _refresh(context):
    """Get the step count data."""
    data = {"stepsGoal": None, "steps": None}
    while True:
        try:
            for_date = datetime.now()
            activity_data = await get_activity(context.db, for_date)
            data["stepsGoal"] = activity_data["goals"]["steps"]
            data["steps"] = activity_data["summary"]["steps"]
            _logger.info("steps goal: %s, steps: %s", data["stepsGoal"], data["steps"])
            await context.post_event("refresh", data)
        except CredentialsError:
            _logger.error("Please run `mirror-config --plugins=activity`")
        except Exception as ex:  # pylint: disable=broad-except
            _logger.exception("Error updating activity data: %s", ex)
        await sleep(REFRESH_INTERVAL.total_seconds())
