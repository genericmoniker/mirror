from datetime import timedelta

from mirror.plugins.calendars.datetime_utils import now_tz


def create_event(
    summary: str = "Test Event",
    start: str = "2024-05-28T19:00:00",
    end: str = "2024-05-28T20:00:00",
    calendar_id: str = "test@test.com",
    calendar_name: str = "Test Calendar",
) -> dict:
    return {
        "summary": summary,
        "start": {"dateTime": start, "timeZone": "America/Denver"},
        "end": {"dateTime": end, "timeZone": "America/Denver"},
        "calendar_id": calendar_id,
        "calendar_name": calendar_name,
    }


def create_all_day_event(
    summary: str = "Test Event",
    start: str = "",
    calendar_id: str = "test@test.com",
    calendar_name: str = "Test Calendar",
) -> dict:
    if not start:
        start = (now_tz() + timedelta(days=3)).strftime("%Y-%m-%d")
    return {
        "summary": summary,
        "start": {"date": start},
        "end": {"date": start},
        "calendar_id": calendar_id,
        "calendar_name": calendar_name,
    }


def now_offset(hours: int) -> str:
    return (now_tz() + timedelta(hours=hours)).isoformat()
