"""Retrieve data from Google Calendar.

Google API references:
https://developers.google.com/calendar/v3/errors?hl=en
https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
"""

import logging

from aiogoogle import Aiogoogle, HTTPError
from aiogoogle.auth import UserCreds
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


_logger = logging.getLogger(__name__)


def obtain_user_permission(client_creds) -> dict:
    """Run the authorization flow to grant permission to access a user's calendar.

    :return: user credentials that can be used when calling `get_events`.
    """
    # We're using Google's synchronous OAuth library here instead of aiogoogle since:
    #
    # 1. Configuration doesn't need or benefit from parallelism
    # 2. This handles the whole flow in just a couple of lines of code
    #
    # The creds dicts are mostly compatible between both libraries, but require some
    #    conversion.
    #
    # TODO: What happens if the user declines?

    # Convert client creds from aiogoogle format:
    client_creds = {"installed": client_creds}

    flow = InstalledAppFlow.from_client_config(client_creds, SCOPES)
    creds = flow.run_local_server(port=0).__getstate__()

    # Convert user creds to aiogoogle format:
    return UserCreds(
        access_token=creds["token"],
        refresh_token=creds["_refresh_token"],
        expires_at=creds["expiry"].isoformat(),
        token_uri=creds["_token_uri"],
    )


def no_filter(_event):
    """An event filter that doesn't filter out any events."""
    return True


async def get_events(user_creds, client_creds, list_args, filter_func=None):
    """List events from all calendars according to the parameters given.

    The supplied credentials dict may be updated if tokens are refreshed.

    :param user_creds: User credentials from `obtain_user_permission`.
    :param client_creds: Client credentials from configuration.
    :param list_args: Arguments to pass to the calendar API's event list
        function.
    :param filter_func: Callable that can filter out individual events.
        The function should return True to include, False to exclude.
    :raise CredentialsError: if the credentials have not been set up,
        or if they have expired.
    """
    filter_func = filter_func or no_filter
    if "access_token" not in user_creds:
        raise CredentialsError

    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        # TODO: Cache service discovery?
        service = await aiogoogle.discover("calendar", "v3")
        try:
            calendar_list = await aiogoogle.as_user(service.calendarList.list())

            # The client library automatically refreshes when fetching data if it can,
            # so update the creds.
            user_creds.update(aiogoogle.user_creds)

            events = []
            for calendar_list_entry in calendar_list["items"]:
                await _add_calendar_events(
                    aiogoogle,
                    service,
                    list_args,
                    calendar_list_entry,
                    events,
                    filter_func,
                )
            return dict(items=sorted(events, key=_event_sort_key_function))
        except HTTPError as ex:
            if "invalid_grant" in str(ex):
                raise CredentialsError from ex
            raise


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


async def _add_calendar_events(
    aiogoogle, service, list_args, calendar, events, filter_func
):
    calendar_id = calendar["id"]
    try:
        events_result = await aiogoogle.as_user(
            service.events.list(calendarId=calendar_id, singleEvents=True, **list_args)
        )
    except Exception as ex:
        # TODO: Some calendars (e.g. "Holidays in United States") get 404 errors here.
        #  Is that because there aren't any events (holidays) in the range, or because
        #  something else is wrong?
        _logger.error(
            'Error getting events from "%s". %s',
            calendar["summary"],
            ex,
        )
    else:
        events += [e for e in events_result.get("items", []) if filter_func(e)]


def _event_sort_key_function(event):
    start = event.get("start", {})
    # start may be specified by either 'date' or 'dateTime'
    return start.get("date", start.get("dateTime", ""))
