import email
from datetime import datetime, timedelta

from flask import Flask
from imapclient import IMAPClient


def fetch_messages(app: Flask):
    """Fetch email messages from the configured IMAP account.

    Only messages from the past 7 days that have "Mirror" in the subject are
    fetched.

    :return: list of dict with:
        {'sender': <sender>, 'body': <body>, 'body_lines': [<lines>]}.
    """
    if not app.config.get("IMAP_HOST"):
        return []
    client = IMAPClient(
        app.config.get("IMAP_HOST"),
        app.config.get("IMAP_PORT"),
    )
    client.login(
        app.config.get("IMAP_USERNAME"),
        app.config.get("IMAP_PASSWORD"),
    )
    client.select_folder("INBOX")
    since = (datetime.now() - timedelta(days=7)).date()
    message_ids = client.search(
        ["SINCE", since.strftime("%d-%b-%Y"), "SUBJECT", "Mirror"]
    )
    raw_messages = client.fetch(message_ids, ["RFC822"])
    client.logout()

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
        result.append(dict(sender=sender, body=body, body_lines=body.splitlines()))
    return result


def _parse_sender_name(message):
    from_ = message["From"]
    return from_.split("<")[0].strip()
