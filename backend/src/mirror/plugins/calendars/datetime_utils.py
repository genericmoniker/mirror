"""Utilities for working with time zones and datetimes."""
import datetime


def now_tz() -> datetime.datetime:
    """Get the current local time as a time zone aware datetime."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.astimezone()


def start_of_day_tz() -> datetime.datetime:
    """Get the start of the current day as a time zone aware datetime."""
    now = now_tz()
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day_tz() -> datetime.datetime:
    """Get the end of the current day as a time zone aware datetime."""
    now = now_tz()
    return now.replace(hour=23, minute=59, second=59, microsecond=9999)


def parse_date_tz(date: str) -> datetime.datetime:
    """Parse an ISO8601 date string returning a time zone aware datetime.

    If you want parsing of times and time zones, try the dateutil package.
    """
    parsed = datetime.datetime.fromisoformat(date)
    return parsed.astimezone()
