"""Plugin management module."""

import contextlib
import logging
from collections.abc import Generator, Iterator

from mirror.event_bus import EventBus
from mirror.plugin_context import PluginContext
from mirror.plugin_discovery import discover_plugins

_logger = logging.getLogger(__name__)


class PluginManager:
    """Class for working with all discovered plugins."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self._discovered_plugins = discover_plugins()
        _logger.info(
            "Discovered plugins: %s",
            ", ".join(plugin.name for plugin in self._discovered_plugins),
        )

    def __iter__(self) -> Iterator:
        """Iterate over the discovered plugins."""
        yield from self._discovered_plugins

    def startup(self) -> None:
        """Start all discovered plugins."""
        for plugin in self._discovered_plugins:
            with plugin_error_logger(plugin.name, "start_plugin"):
                plugin.startup(PluginContext(plugin, self._event_bus))

    def shutdown(self) -> None:
        """Stop all discovered plugins."""
        for plugin in self._discovered_plugins:
            with plugin_error_logger(plugin.name, "stop_plugin"):
                plugin.shutdown(PluginContext(plugin, self._event_bus))

    def render_widget(self, widget_name: str, n: int | None = None) -> str:
        plugin_name, _, widget_name = widget_name.partition("-")
        for plugin in self._discovered_plugins:
            if plugin.name == plugin_name:
                return plugin.render(context=None, widget=widget_name, n=n)
        msg = f"Unknown plugin: {plugin_name}"
        raise ValueError(msg)


@contextlib.contextmanager
def plugin_error_logger(name: str, action: str) -> Generator:
    try:
        yield
    except Exception as ex:  # noqa: BLE001
        _logger.error(  # noqa: TRY400
            "Error from plugin '%s' (%s): %s",
            name,
            action,
            ex,
        )
