"""Common code for calendars plugin."""

import asyncio
import logging
import secrets
from collections.abc import Callable, Iterable
from datetime import datetime

from mirror.plugin_context import PluginContext

from .google_calendar import CredentialsError, build_auth_url

_logger = logging.getLogger(__name__)

# DB key for stored OAuth tokens:
USER_CREDENTIALS = "user-creds"
OAUTH_STATE_KEY = "oauth_state"

# config keys (mirror.toml [plugin.calendars]):
COMING_UP_FILTER = "coming_up_filter"
SUBORDINATE_FILTER = "subordinate_filter"


_credentials_lock = asyncio.Lock()


class Event(dict):  # noqa: PLW1641
    """Event after reshaping for the client."""

    def __eq__(self, value: object) -> bool:
        """Equality comparison that ignores the calendar_id and calendar_name."""
        if not isinstance(value, dict):
            return False
        this = self | {"calendar_id": None, "calendar_name": None}
        that = value | {"calendar_id": None, "calendar_name": None}
        return this == that


def range_to_list_args(event_range_func: Callable) -> dict:
    start, stop = event_range_func()
    return {"timeMin": start, "timeMax": stop}


def get_auth_url(context: PluginContext) -> str:
    """Generate a Google OAuth2 authorization URL and store the state in the DB."""
    state = context.db.get(OAUTH_STATE_KEY)
    if not state:
        state = secrets.token_urlsafe(16)
        context.db[OAUTH_STATE_KEY] = state
    return build_auth_url(context.config["client_id"], state)


async def refresh_data(
    context: PluginContext,
    get_events: Callable,
    list_args: dict,
    filter_func: Callable | None = None,
) -> dict:
    """Refresh calendar events.

    :param context: PluginContext for user creds (db) and client creds (config).
    :param get_events: Callable that can fetch events from a calendar service.
    :param list_args: Arguments to pass to the `get_events` callable.
    :param filter_func: Callable that can filter out individual events. The function
        should accept an event and return True to include it or False to exclude it. If
        unspecified, all events will be included.
    :return: dict with a list of events in "items", or {"items": [], "login_required":
        True} if credentials are missing or invalid.
    """
    try:
        # Lock so that only one caller needs to refresh the creds, which happens
        # behind the scenes when we call `get_events`.
        async with _credentials_lock:
            user_creds = context.db.get(USER_CREDENTIALS)
            client_creds = {
                "client_id": context.config.get("client_id"),
                "client_secret": context.config.get("client_secret"),
            }
            if user_creds is None or not client_creds["client_id"]:
                raise CredentialsError  # noqa: TRY301
            events = await get_events(
                user_creds,
                client_creds,
                list_args,
            )

            # Save potentially refreshed user creds.
            context.db[USER_CREDENTIALS] = user_creds

        filter_func = filter_func or _no_filter
        return reshape_events(e for e in events if filter_func(e))

    except CredentialsError:
        return {"items": [], "login_required": True}


def _no_filter(_event: dict) -> bool:
    """Allow all events."""
    return True


def reshape_events(events: Iterable[dict]) -> dict:
    """Optimize events for clients."""
    items = []
    for event in events:
        _event_to_local_time(event)
        new_event = Event(
            summary=event.get("summary", "(no summary)"),
            start=event["start"],
            end=event["end"],
            calendar_id=event["calendar_id"],
            calendar_name=event["calendar_name"],
        )

        # Only include one event if it is duplicated across calendars. This overlaps
        # conceptually with the `filter_func` in `refresh_data` but considering all
        # events rather than just one.
        if new_event not in items:
            items.append(new_event)

    return {"items": items}


def _event_to_local_time(event: dict) -> None:
    """Convert event start and end time strings to a local datetime, in-place.

    For all-day events, no conversion is done.

    Example event start and end format (for time-specific events):

    {'dateTime': '2026-01-04T12:00:00-07:00', 'timeZone': 'America/Denver'}

    or (for all-day events, no time zone at all):

    {'date': '2026-01-04'}

    Note that dateTime includes the time zone offset, but there is also a timeZone
    field, so we can know the original time zone if needed.
    """
    start = event["start"]
    end = event["end"]
    if "dateTime" in event["start"]:
        start_dt = datetime.fromisoformat(event["start"]["dateTime"]).astimezone()
        end_dt = datetime.fromisoformat(event["end"]["dateTime"]).astimezone()
        start["dateTime"] = start_dt
        end["dateTime"] = end_dt
