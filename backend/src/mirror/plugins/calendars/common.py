import asyncio
import logging

from .google_calendar import CredentialsError, get_events

_logger = logging.getLogger(__name__)

# database keys:
CLIENT_CREDENTIALS = "client-creds"
USER_CREDENTIALS = "user-creds"
COMING_UP_FILTER = "coming-up-filter"


def range_to_list_args(event_range_func):
    start, stop = event_range_func()
    return {"timeMin": start, "timeMax": stop}


async def refresh_data(db, list_args, filter_func=None):
    try:
        # Lock so that only one caller needs to refresh the creds, which happens
        # behind the scenes when we call `get_events`.
        async with asyncio.Lock():
            user_creds = db.get(USER_CREDENTIALS)
            client_creds = db.get(CLIENT_CREDENTIALS)
            if user_creds is None or client_creds is None:
                raise CredentialsError
            events = await get_events(user_creds, client_creds, list_args, filter_func)

            # Save potentially refreshed user creds.
            db[USER_CREDENTIALS] = user_creds

        return reshape_events(events)

    except CredentialsError as ex:
        _logger.error("Please run `mirror-config --plugins=calendars` (%s)", ex)


def reshape_events(events):
    """Optimize events for clients."""
    items = []
    for event in events["items"]:

        # Some people enter calendar events in ALL CAPS, which is annoying 😉.
        summary = event["summary"]
        if summary.isupper():
            summary = summary.title()

        new_event = {"summary": summary, "start": event["start"]}

        # Only include one event if it is duplicated across calendars. This overlaps
        # conceptually with the `filter_func` on `refresh_data` but considering all
        # events rather than just one.
        if new_event not in items:
            items.append(new_event)

    return {"items": items}
