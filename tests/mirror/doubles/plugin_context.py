"""A test double for the PluginContext class."""
from dataclasses import dataclass


@dataclass
class WidgetUpdate:
    """A widget update."""

    widget_name: str
    data: dict


class PluginContext:
    """A PluginContext test double."""

    def __init__(self) -> None:
        self.db = {}
        self.updates = []

    @property
    def update(self) -> WidgetUpdate | None:
        """Return the most recent widget update."""
        assert self.updates, "No widget updates"
        return self.updates[-1]

    async def widget_updated(self, data: dict, widget_name: str | None = None) -> None:
        """Indicate that a widget has been updated."""
        self.updates.append(WidgetUpdate(widget_name, data))
