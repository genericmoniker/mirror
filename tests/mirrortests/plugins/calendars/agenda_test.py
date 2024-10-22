"""Tests for the agenda widget of the calendars plugin."""

from datetime import timedelta

import pytest
from mirror.plugins.calendars import agenda
from mirror.plugins.calendars.common import (
    CLIENT_CREDENTIALS,
    SUBORDINATE_FILTER,
    USER_CREDENTIALS,
)
from mirror.plugins.calendars.datetime_utils import now_tz

from mirrortests.doubles.plugin_context import PluginContext


@pytest.fixture()
def context() -> PluginContext:
    context = PluginContext()
    context.db[USER_CREDENTIALS] = "fake user creds"
    context.db[CLIENT_CREDENTIALS] = "fake client creds"
    return context


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


def now_offset(hours: int) -> str:
    return (now_tz() + timedelta(hours=hours)).isoformat()


async def test_widget_updated(context: PluginContext) -> None:
    """The widget is updated with a calendar item on refresh."""

    async def get_events(*_args, **_kwargs) -> list[dict]:
        return [create_event("Test Event")]

    await agenda.refresh(context, get_events)

    assert context.update.widget_name == "agenda"
    assert context.update.data["items"][0]["summary"] == "Test Event"


async def test_duplicates_collapsed(context: PluginContext) -> None:
    """Duplicate events on different calendars are collapsed into a single item."""

    async def get_events(*_args, **_kwargs) -> list[dict]:
        return [
            create_event(calendar_id="foo@test.com"),
            create_event(calendar_id="bar@test.com"),
        ]

    await agenda.refresh(context, get_events)

    assert len(context.update.data["items"]) == 1


async def test_current_event(context: PluginContext) -> None:
    """An event happening right now is marked as current."""

    async def get_events(*_args, **_kwargs) -> list[dict]:
        return [
            create_event("Past", start=now_offset(hours=-2), end=now_offset(hours=-1)),
            create_event("Now", start=now_offset(hours=-1), end=now_offset(hours=1)),
            create_event("Future", start=now_offset(hours=1), end=now_offset(hours=2)),
        ]

    await agenda.refresh(context, get_events)

    past = context.update.data["items"][0]
    assert past["summary"] == "Past"
    assert past["current"] is False

    now = context.update.data["items"][1]
    assert now["summary"] == "Now"
    assert now["current"] is True

    future = context.update.data["items"][2]
    assert future["summary"] == "Future"
    assert future["current"] is False


async def test_subordinate_filter(context: PluginContext) -> None:
    """Events on subordinate calendars are marked as such."""

    context.db[SUBORDINATE_FILTER] = "adria|caleen"

    async def get_events(*_args, **_kwargs) -> list[dict]:
        return [
            create_event("Subordinate 1", calendar_id="adria@test.com"),
            create_event("Not Subordinate", calendar_id="bix@test.com"),
            create_event("Subordinate 2", calendar_id="caleen@test.com"),
        ]

    await agenda.refresh(context, get_events)

    items = context.update.data["items"]
    sub_1 = next(item for item in items if item["summary"] == "Subordinate 1")
    assert sub_1["subordinate"] is True
    non_sub = next(item for item in items if item["summary"] == "Not Subordinate")
    assert non_sub["subordinate"] is False
    sub_2 = next(item for item in items if item["summary"] == "Subordinate 2")
    assert sub_2["subordinate"] is True


async def test_meals_filter(context: PluginContext) -> None:
    """Events on the "dinner" or "meals" calendars are marked as such."""

    async def get_events(*_args, **_kwargs) -> list[dict]:
        return [
            create_event("Tacos", calendar_name="Dinner"),
            create_event("Pizza", calendar_name="Meals"),
            create_event("Not Dinner", calendar_name="Not Dinner"),
        ]

    await agenda.refresh(context, get_events)

    items = context.update.data["items"]
    tacos = next(item for item in items if item["summary"] == "Tacos")
    assert tacos["meals"] is True
    pizza = next(item for item in items if item["summary"] == "Pizza")
    assert pizza["meals"] is True
    not_dinner = next(item for item in items if item["summary"] == "Not Dinner")
    assert not_dinner["meals"] is False
