"""Plugin management module."""
import contextlib
import logging
from collections.abc import Generator

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
            ", ".join(self._discovered_plugins.keys()),
        )

    def startup(self) -> None:
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "start_plugin"):
                module.start_plugin(PluginContext(name, self._event_bus))

    def shutdown(self) -> None:
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "stop_plugin"):
                module.stop_plugin(PluginContext(name, self._event_bus))


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
