import logging
from functools import partial

import uvicorn
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from mirror.event_bus import EventBus
from mirror.log import setup_logging
from mirror.plugin_context import PluginContext
from mirror.plugin_discovery import discover_plugins

_logger = logging.getLogger(__name__)


async def load_plugins(event_bus):
    plugins = discover_plugins()
    loaded_plugins = list(plugins.keys())
    for name, module in plugins.items():
        try:
            module.start_plugin(PluginContext(name, event_bus))
        except Exception as ex:  # pylint:disable=broad-except
            _logger.error("Failed to load plugin '%s': %s", name, ex)
            loaded_plugins.remove(name)
    _logger.info("Loaded plugins: %s", ", ".join(loaded_plugins))


async def stream_events(request):
    event_bus = request.app.state.event_bus
    return EventSourceResponse(event_bus.listen_for_events())


def create_app():
    setup_logging()

    routes = [
        Route("/events", endpoint=stream_events),
        Mount("/", StaticFiles(directory="static", html=True)),
    ]

    event_bus = EventBus()
    load_plugins_partial = partial(load_plugins, event_bus)

    application = Starlette(
        debug=True,
        routes=routes,
        on_startup=[load_plugins_partial],
        on_shutdown=[event_bus.shutdown],
    )
    application.state.event_bus = event_bus

    return application


# The app object is created globally so that this module can run under an
# application server other than uvicorn, such as Gunicorn.
app = create_app()


def main():
    uvicorn.run(app, port=5000)


if __name__ == "__main__":
    main()
