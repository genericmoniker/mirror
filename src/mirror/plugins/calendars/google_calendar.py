"""Retrieve data from Google Calendar.

Google API references
=====================

https://developers.google.com/calendar/v3/errors?hl=en

https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/

Refresh tokens:
https://developers.google.com/identity/protocols/oauth2#expiration
"""

import logging
from typing import Any

from aiogoogle import Aiogoogle, HTTPError
from aiogoogle.auth import UserCreds
from aiogoogle.auth.creds import ClientCreds
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


_logger = logging.getLogger(__name__)


def obtain_user_permission(client_creds: dict) -> dict:
    """Run the authorization flow to grant permission to access a user's calendar.

    If the user doesn't authorize the application, this will just block...

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
        token_type="Bearer",
    )


async def get_events(
    user_creds: dict,
    client_creds: dict,
    list_args: dict,
) -> list[dict]:
    """List events from all calendars according to the parameters given.

    The supplied credentials dict may be updated if tokens are refreshed.

    :param user_creds: User credentials from `obtain_user_permission`.
    :param client_creds: Client credentials from configuration.
    :param list_args: Arguments to pass to the calendar API's event list
        function.
    :return: List of event dicts.
    :raise CredentialsError: if the credentials have not been set up,
        or if they have expired.
    """
    if "access_token" not in user_creds:
        msg = "No access token in user credentials."
        raise CredentialsError(msg)

    # Convert to aiogoogle format
    user_creds = UserCreds(**user_creds)
    client_creds = ClientCreds(
        client_id=client_creds["client_id"],
        client_secret=client_creds["client_secret"],
        scopes=SCOPES,
    )

    async with Aiogoogle(user_creds=user_creds, client_creds=client_creds) as aiogoogle:
        # Is there a way to cache service discovery?
        service = await aiogoogle.discover("calendar", "v3")
        try:
            calendar_list = await aiogoogle.as_user(
                service.calendarList.list(),
                timeout=30,
            )
            _update_user_creds(user_creds, aiogoogle.user_creds)

            events = []
            for calendar_list_entry in calendar_list["items"]:
                events += await _get_calendar_events(
                    aiogoogle,
                    service,
                    list_args,
                    calendar_list_entry,
                )
            return sorted(events, key=_event_sort_key_function)
        except HTTPError as ex:
            if "invalid_grant" in str(ex):
                msg = "User credentials rejected."
                raise CredentialsError(msg) from ex
            raise


class CredentialsError(Exception):
    """Credentials are invalid (e.g. empty or expired)."""


async def _get_calendar_events(
    aiogoogle: Aiogoogle,
    service: Any,  # noqa: ANN401
    list_args: dict,
    calendar: dict,
) -> list[dict]:
    calendar_id = calendar["id"]
    try:
        events_result = await aiogoogle.as_user(
            service.events.list(calendarId=calendar_id, singleEvents=True, **list_args),
            timeout=30,
        )
    except HTTPError as ex:
        _logger.error(  # noqa: TRY400
            'Error getting events from "%s". %s',
            calendar["summary"],
            ex,
        )
        return []
    else:
        return [
            e | {"calendar_id": calendar_id} for e in events_result.get("items", [])
        ]


def _event_sort_key_function(event: dict) -> str:
    start = event.get("start", {})
    # start may be specified by either 'date' or 'dateTime'
    return start.get("date", start.get("dateTime", ""))


def _update_user_creds(existing_creds: UserCreds, new_creds: UserCreds | None) -> None:
    # Don't just `update` the existing creds with the new ones -- that will overwrite
    # the refresh-related fields with None because the creds received after refreshing
    # don't include them. It seems odd that `aiogoogle.as_user` effectively wipes out
    # refresh capability after a refresh is done (may be considered a bug?).
    if new_creds is None:
        return
    existing_creds["access_token"] = new_creds["access_token"]
    existing_creds["expires_in"] = new_creds["expires_in"]
    existing_creds["expires_at"] = new_creds["expires_at"]
    existing_creds["token_type"] = new_creds["token_type"]
