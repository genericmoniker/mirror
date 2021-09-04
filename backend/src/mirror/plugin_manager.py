import contextlib
import logging

from mirror.plugin_context import PluginContext
from mirror.plugin_discovery import discover_plugins

_logger = logging.getLogger(__name__)


class PluginManager:
    """Class for working with all discovered plugins."""

    def __init__(self, event_bus) -> None:
        self._event_bus = event_bus
        self._discovered_plugins = discover_plugins()
        _logger.info(
            "Discovered plugins: %s", ", ".join(self._discovered_plugins.keys())
        )

    def startup(self):
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "start_plugin"):
                module.start_plugin(PluginContext(name, self._event_bus))

    def shutdown(self):
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "stop_plugin"):
                module.stop_plugin(PluginContext(name, self._event_bus))

    def dump_tasks(self):
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "dump_tasks"):
                module.dump_tasks(PluginContext(name, self._event_bus))


@contextlib.contextmanager
def plugin_error_logger(name, action):
    try:
        yield
    except AttributeError:
        pass  # plugin entrypoints are optional
    except Exception as ex:  # pylint:disable=broad-except
        _logger.error("Error from plugin '%s' (%s): %s", name, action, ex)
