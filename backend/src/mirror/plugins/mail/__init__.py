"""Mail plugin using IMAP to read messages.

This is currently implemented using the imapclient package, which is blocking, so calls
to the server are done with run_in_executor.

At the time of writing, there *is* an asyncio IMAP library, aioimaplib, but it suffers
from the same problem as the standard library's imaplib: It is too low-level for easy
use. Comparatively, imapclient is a joy to use.
"""
import asyncio
import email
import functools
import logging
import socket
from collections.abc import Callable
from datetime import datetime, timedelta
from getpass import getpass

from imapclient import IMAPClient
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_context import PluginContext

# database keys
IMAP_HOST = "IMAP_HOST"
IMAP_PORT = "IMAP_PORT"
IMAP_USERNAME = "IMAP_USERNAME"
IMAP_PASSWORD = "IMAP_PASSWORD"

REFRESH_INTERVAL = timedelta(minutes=5)

_logger = logging.getLogger(__name__)
_state = {}


def configure_plugin(config_context: PluginConfigureContext) -> None:
    db = config_context.db
    print("Mail Plugin Set Up")

    db[IMAP_HOST] = input("IMAP email server host: ").strip()
    db[IMAP_PORT] = input("IMAP email server port: ").strip()
    db[IMAP_USERNAME] = input("Email username: ").strip()
    db[IMAP_PASSWORD] = getpass("Email password: ").strip()


def start_plugin(context: PluginContext) -> None:
    task = asyncio.create_task(_refresh(context), name="mail.refresh")
    _state["task"] = task


def stop_plugin(context: PluginContext) -> None:  # noqa: ARG001
    task = _state.get("task")
    if task:
        task.cancel()


async def _refresh(context: PluginContext) -> None:
    while True:
        try:
            emails = await _fetch_messages(context.db)
            data = {"items": emails}
            await context.post_event("refresh", data)
            context.vote_connected()
        except (OSError, socket.timeout) as ex:
            # https://imapclient.readthedocs.io/en/2.2.0/api.html#exceptions
            context.vote_disconnected(ex)
            _logger.exception("Network error getting emails.")
        except Exception:
            _logger.exception("Error getting emails.")
        await asyncio.sleep(REFRESH_INTERVAL.total_seconds())


def run_in_executor(func: Callable) -> Callable:
    @functools.wraps(func)
    def inner(*args, **kwargs) -> asyncio.Future:
        loop = asyncio.get_running_loop()
        return loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return inner


@run_in_executor
def _fetch_messages(db: dict) -> list[dict[str, str]]:
    """Fetch email messages from the configured IMAP account.

    Only messages from the past week that have "Mirror" in the subject are
    fetched.

    :return: list of dict with:
        {'sender': <sender>, 'body': <body>, 'body_lines': [<lines>]}.
    """
    if not db.get(IMAP_HOST):
        return []
    with IMAPClient(host=db.get(IMAP_HOST), port=db.get(IMAP_PORT)) as client:
        client.login(db.get(IMAP_USERNAME), db.get(IMAP_PASSWORD))
        client.select_folder("INBOX")
        since = (datetime.now() - timedelta(days=6)).date()  # noqa: DTZ005
        message_ids = client.search(
            ["SINCE", since.strftime("%d-%b-%Y"), "SUBJECT", "Mirror"],
        )
        raw_messages = client.fetch(message_ids, ["RFC822"])

    result = []
    for raw in raw_messages.values():
        message = email.message_from_bytes(raw[b"RFC822"])
        sender = _parse_sender_name(message)
        if message.is_multipart():
            parts = message.get_payload()
            for part in parts:
                if part.get_content_type() == "text/plain":
                    message = part
                    break
            else:
                message = parts[0]
        body = message.get_payload(decode=True).decode()
        result.append({"sender": sender, "body": body, "body_lines": body.splitlines()})
    return result


def _parse_sender_name(message: email.message.Message) -> str:
    from_ = message["From"]
    return from_.split("<")[0].strip()
