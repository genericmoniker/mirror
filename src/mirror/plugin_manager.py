import contextlib
import logging

from starlette.routing import Mount
from starlette.staticfiles import StaticFiles

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

    def get_scripts(self):
        scripts = {}
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "get_scripts"):
                if hasattr(module, "get_scripts"):
                    scripts[name] = module.get_scripts()
        return scripts

    def get_routes(self):
        routes = []
        for name, _ in self._discovered_plugins.items():
            with plugin_error_logger(name, "get_routes"):
                routes.append(
                    Mount(
                        "/" + name,
                        StaticFiles(packages=["mirror.plugins." + name]),
                        name=name,
                    )
                )
        return routes

    def startup(self):
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "start_plugin"):
                if hasattr(module, "start_plugin"):
                    module.start_plugin(PluginContext(name, self._event_bus))

    def shutdown(self):
        for name, module in self._discovered_plugins.items():
            with plugin_error_logger(name, "stop_plugin"):
                if hasattr(module, "stop_plugin"):
                    module.stop_plugin(PluginContext(name, self._event_bus))


@contextlib.contextmanager
def plugin_error_logger(name, action):
    try:
        yield
    except Exception as ex:  # pylint:disable=broad-except
        _logger.error("Error from plugin '%s' (%s): %s", name, action, ex)
