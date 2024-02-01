"""Step count from the Fitbit API."""
import logging
from asyncio import create_task, sleep
from datetime import datetime, timedelta

from httpx import TransportError
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_context import PluginContext

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


def configure_plugin(config_context: PluginConfigureContext) -> None:
    # See README.md for detailed instructions.
    db = config_context.db
    db.clear()
    print("Activity Plugin Set Up")
    people_count = int(input("How many people? ").strip())
    for i in range(people_count):
        _get_person_creds(db, i + 1)


def _get_person_creds(db: dict, person_num: int) -> None:
    print(f"Person #{person_num}")
    name = input("Name (to display): ").strip()
    client_id = input("Fitbit client ID (from app registration): ").strip()
    client_secret = input("Fitbit client secret (from app registration): ").strip()
    auth_code = input("Authorization code (from user grant URL): ").strip()

    # In case of copy-paste errors, strip these too.
    auth_code = auth_code.strip("#_=_")  # noqa: B005

    creds = {}
    creds[CLIENT_ID] = client_id
    creds[CLIENT_SECRET] = client_secret
    creds[AUTHORIZATION_CODE] = auth_code
    creds[ACCESS_TOKEN] = ""
    creds[REFRESH_TOKEN] = ""

    # Need to assign dict all at once; the DB can't detect nested changes.
    db[name] = creds


def start_plugin(context: PluginContext) -> None:
    task = create_task(_refresh(context), name="activity.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    """Get the step count data."""
    names = sorted(context.db)
    data = {
        "persons": [
            {"name": name, "steps_goal": None, "steps": None, "percent": 0.0}
            for name in names
        ],
    }
    while True:
        try:
            for_date = datetime.now().astimezone()
            for i, name in enumerate(names):
                person = data["persons"][i]
                creds = context.db[name]
                activity_data = await get_activity(creds, for_date)
                context.db[name] = creds  # potentially update creds
                person["steps_goal"] = activity_data["goals"]["steps"]
                person["steps"] = activity_data["summary"]["steps"]
                person["percent"] = person["steps"] / person["steps_goal"]
                _logger.info(
                    "%s steps goal: %s, steps: %s (%s%%)",
                    name,
                    person["steps_goal"],
                    person["steps"],
                    round(person["percent"] * 100, 2),
                )
            await context.widget_updated(data)
            context.vote_connected()
        except CredentialsError:
            _logger.error(  # noqa: TRY400
                "Please run `mirror-config --plugins=activity`",
            )
        except TransportError as ex:
            # https://www.python-httpx.org/exceptions/
            context.vote_disconnected(ex)
            _logger.exception("Network error updating activity data.")
        except Exception:
            _logger.exception("Error updating activity data.")
        await sleep(REFRESH_INTERVAL.total_seconds())
