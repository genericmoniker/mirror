"""A test double for the PluginContext class."""

from dataclasses import dataclass

from mirror.plugin_context import PluginContext as BasePluginContext


@dataclass
class WidgetUpdate:
    """A widget update."""

    widget_name: str | None
    data: dict


class PluginContext(BasePluginContext):
    """A PluginContext test double."""

    def __init__(self) -> None:
        self.db = {}
        self.updates = []

    @property
    def update(self) -> WidgetUpdate:
        """Return the most recent widget update."""
        assert self.updates, "No widget updates"
        return self.updates[-1]

    async def widget_updated(self, data: dict, widget_name: str | None = None) -> None:
        """Indicate that a widget has been updated."""
        self.updates.append(WidgetUpdate(widget_name, data))
