"""Utilities for working with time zones and datetimes."""
import datetime


def now_tz() -> datetime.datetime:
    """Get the current local time as a time zone aware datetime."""
    now = datetime.datetime.now(datetime.UTC)
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


def short_relative_time(time: datetime.datetime) -> str:
    """Get a short relative time string from the given datetime.

    Short in length, and in the time range it is good for.

    Doesn't currently handle dates in the past.
    """
    tomorrow_start = start_of_day_tz() + datetime.timedelta(days=1)
    tomorrow_end = end_of_day_tz() + datetime.timedelta(days=1)
    if tomorrow_start <= time <= tomorrow_end:
        return "tomorrow"
    return time.strftime("%a")


def relative_time(time: datetime.datetime) -> str:  # noqa: PLR0911
    """Get a relative time string from the given datetime.

    Doesn't currently handle dates in the past.
    """
    tomorrow_start = start_of_day_tz() + datetime.timedelta(days=1)
    tomorrow_end = end_of_day_tz() + datetime.timedelta(days=1)
    if tomorrow_start <= time <= tomorrow_end:
        return "tomorrow"
    delta = time - now_tz()
    if delta < datetime.timedelta(days=7):
        return "on " + time.strftime("%A")
    if delta < datetime.timedelta(days=14):
        return "next " + time.strftime("%A")
    if delta < datetime.timedelta(days=21):
        return "in a couple of weeks"
    if delta < datetime.timedelta(days=28):
        return "in a few weeks"
    if delta < datetime.timedelta(days=60):
        return "in a month"
    if delta < datetime.timedelta(days=90):
        return "in a couple of months"
    if delta < datetime.timedelta(days=180):
        return "in a few months"
    if delta < datetime.timedelta(days=365):
        return "in several months"
    return "in a long time from now"
