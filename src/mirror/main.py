import logging

import uvicorn
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from mirror import event_bus
from mirror.log import setup_logging
from mirror.plugin_context import PluginContext
from mirror.plugin_discovery import discover_plugins

_logger = logging.getLogger(__name__)


async def load_plugins():
    plugins = discover_plugins()
    loaded_plugins = list(plugins.keys())
    for name, module in plugins.items():
        try:
            module.start_plugin(PluginContext(name))
        except Exception:  # pylint:disable=broad-except
            _logger.exception("Failed to load plugin '%s'", name)
            loaded_plugins.remove(name)
    _logger.info("Loaded plugins: %s", ", ".join(loaded_plugins))


async def stream_events(request):
    return EventSourceResponse(event_bus.event_generator(request))


def create_app():
    setup_logging()

    routes = [
        Route("/events", endpoint=stream_events),
        Mount("/", StaticFiles(directory="static", html=True)),
    ]

    application = Starlette(
        debug=True,
        routes=routes,
        on_startup=[load_plugins, event_bus.start],
        on_shutdown=[event_bus.shutdown],
    )

    return application


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, port=5000)
else:
    app = create_app()
