from mirror.plugins.calendars import coming_up
from mirror.plugins.calendars.common import SUBORDINATE_FILTER
from mirrortests.doubles.plugin_context import PluginContext
from mirrortests.plugins.calendars.common import create_all_day_event


async def test_subordinate_filter(context: PluginContext) -> None:
    """Events on subordinate calendars are marked as such."""

    context.db[SUBORDINATE_FILTER] = "adria|caleen"

    async def get_events(*_args, **_kwargs) -> list[dict]:
        return [
            create_all_day_event("Subordinate 1", calendar_id="adria@test.com"),
            create_all_day_event("Not Subordinate", calendar_id="bix@test.com"),
            create_all_day_event("Subordinate 2", calendar_id="caleen@test.com"),
        ]

    await coming_up.refresh(context, get_events)

    items = context.update.data["items"]
    sub_1 = next(item for item in items if item["summary"] == "Subordinate 1")
    assert sub_1["subordinate"] is True
    non_sub = next(item for item in items if item["summary"] == "Not Subordinate")
    assert non_sub["subordinate"] is False
    sub_2 = next(item for item in items if item["summary"] == "Subordinate 2")
    assert sub_2["subordinate"] is True
