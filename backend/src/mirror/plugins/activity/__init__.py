"""Step count from the Fitbit API."""
import logging
from asyncio import create_task, sleep
from datetime import datetime, timedelta

from httpx import TransportError

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


def configure_plugin(config_context):
    # See README.md for detailed instructions.
    db = config_context.db
    db.clear()
    print("Activity Plugin Set Up")
    people_count = int(input("How many people? ").strip())
    for i in range(people_count):
        _get_person_creds(db, i + 1)


def _get_person_creds(db, person_num):
    print(f"Person #{person_num}")
    name = input("Name (to display): ").strip()
    client_id = input("Fitbit client ID (from app registration): ").strip()
    client_secret = input("Fitbit client secret (from app registration): ").strip()
    auth_code = input("Authorization code (from user grant URL): ").strip()

    # In case of copy-paste errors, strip these too.
    auth_code = auth_code.strip("#_=_")

    creds = {}
    creds[CLIENT_ID] = client_id
    creds[CLIENT_SECRET] = client_secret
    creds[AUTHORIZATION_CODE] = auth_code
    creds[ACCESS_TOKEN] = None
    creds[REFRESH_TOKEN] = None

    # Need to assign dict all at once; the DB can't detect nested changes.
    db[name] = creds


def start_plugin(context):
    task = create_task(_refresh(context), name="activity.refresh")
    _state["task"] = task


def stop_plugin(context):  # pylint: disable=unused-argument
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context):
    """Get the step count data."""
    data = {name: {"stepsGoal": None, "steps": None} for name in context.db}
    while True:
        try:
            for_date = datetime.now()
            for name in context.db:
                creds = context.db[name]
                activity_data = await get_activity(creds, for_date)
                context.db[name] = creds  # potentially update creds
                data[name]["stepsGoal"] = activity_data["goals"]["steps"]
                data[name]["steps"] = activity_data["summary"]["steps"]
                _logger.info(
                    "%s steps goal: %s, steps: %s",
                    name,
                    data[name]["stepsGoal"],
                    data[name]["steps"],
                )
            await context.post_event("refresh", data)
            context.vote_connected()
        except CredentialsError:
            _logger.error("Please run `mirror-config --plugins=activity`")
        except TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error updating activity data.")
        except Exception:  # pylint: disable=broad-except
            _logger.exception("Error updating activity data.")
        await sleep(REFRESH_INTERVAL.total_seconds())
