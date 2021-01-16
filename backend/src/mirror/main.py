import logging
from pathlib import Path

import uvicorn
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from mirror.event_bus import EventBus
from mirror.log import setup_logging
from mirror.plugin_manager import PluginManager

_logger = logging.getLogger(__name__)


async def stream_events(request):
    event_bus = request.app.state.event_bus
    headers = {"Access-Control-Allow-Origin": "http://localhost:5001"}
    return EventSourceResponse(event_bus.listen_for_events(), headers=headers)


def create_app():
    setup_logging()

    event_bus = EventBus()
    plugins = PluginManager(event_bus)
    static_dir = (
        Path(__file__).resolve().parent.parent.parent.parent / "frontend/public"
    )

    routes = [
        Route("/events", endpoint=stream_events),
        Mount("/", StaticFiles(directory=static_dir, html=True), name="static"),
    ]

    application = Starlette(
        debug=True,
        routes=routes,
        on_startup=[plugins.startup],
        on_shutdown=[plugins.shutdown, event_bus.shutdown],
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
