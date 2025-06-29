"""Common code for calendars plugin."""

import asyncio
import logging
from collections.abc import Callable, Iterable

from .google_calendar import CredentialsError

_logger = logging.getLogger(__name__)

# database keys:
CLIENT_CREDENTIALS = "client-creds"
USER_CREDENTIALS = "user-creds"
COMING_UP_FILTER = "coming-up-filter"
SUBORDINATE_FILTER = "subordinate-filter"


class Event(dict):
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


async def refresh_data(
    db: dict,
    get_events: Callable,
    list_args: dict,
    filter_func: Callable | None = None,
) -> dict:
    """Refresh calendar events.

    :param db: Database dict.
    :param get_events: Callable that can fetch events from a calendar service.
    :param list_args: Arguments to pass to the `get_events_func`.
    :param filter_func: Callable that can filter out individual events. The function
        should accept an event and return True to include it or False to exclude it. If
        unspecified, all events will be included.
    :return: dict with a list of events in "items", which may be empty if credentials
        are missing or invalid.
    """
    try:
        # Lock so that only one caller needs to refresh the creds, which happens
        # behind the scenes when we call `get_events`.
        async with asyncio.Lock():
            user_creds = db.get(USER_CREDENTIALS)
            client_creds = db.get(CLIENT_CREDENTIALS)
            if user_creds is None or client_creds is None:
                raise CredentialsError  # noqa: TRY301
            events = await get_events(
                user_creds,
                client_creds,
                list_args,
            )

            # Save potentially refreshed user creds.
            db[USER_CREDENTIALS] = user_creds

        filter_func = filter_func or _no_filter
        return reshape_events(e for e in events if filter_func(e))

    except CredentialsError:
        _logger.error("Please run `mirror-config --plugins=calendars`")  # noqa: TRY400
        return {"items": []}


def _no_filter(_event: dict) -> bool:
    """Allow all events."""
    return True


def reshape_events(events: Iterable[dict]) -> dict:
    """Optimize events for clients."""
    items = []
    for event in events:
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
