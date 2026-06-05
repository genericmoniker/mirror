"""Retrieve data from Google Calendar.

Google API references
=====================

https://developers.google.com/calendar/v3/errors?hl=en

https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/

Refresh tokens:
https://developers.google.com/identity/protocols/oauth2#expiration
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx2
from aiogoogle import Aiogoogle, HTTPError
from aiogoogle.auth import UserCreds
from aiogoogle.auth.creds import ClientCreds

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
REDIRECT_URI = "http://localhost:5000/oauth/calendars"


_logger = logging.getLogger(__name__)


def build_auth_url(client_id: str, state: str) -> str:
    """Build the Google OAuth2 authorization URL."""
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    return GOOGLE_AUTH_URL + "?" + urlencode(params)


async def exchange_code_for_creds(
    client_id: str, client_secret: str, code: str
) -> dict:
    """Exchange an authorization code for user credentials."""
    async with httpx2.AsyncClient(timeout=10) as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": client_id,
                "client_secret": client_secret,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        response.raise_for_status()
        token_data = response.json()

    expires_at = (
        datetime.now(UTC) + timedelta(seconds=token_data["expires_in"])
    ).isoformat()

    return dict(
        UserCreds(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            expires_at=expires_at,
            token_uri=GOOGLE_TOKEN_URL,
            token_type="Bearer",
        )
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
    calendar_name = calendar.get("summary", calendar_id)
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
            e | {"calendar_id": calendar_id, "calendar_name": calendar_name}
            for e in events_result.get("items", [])
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
