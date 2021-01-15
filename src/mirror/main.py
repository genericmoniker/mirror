import logging

import uvicorn
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from mirror.event_bus import EventBus
from mirror.log import setup_logging
from mirror.plugin_manager import PluginManager

_logger = logging.getLogger(__name__)


async def homepage(request):
    templates = Jinja2Templates(directory="templates")
    plugin_scripts = request.app.state.plugins.get_scripts()
    return templates.TemplateResponse(
        "index.html", {"request": request, "plugin_scripts": plugin_scripts}
    )


async def stream_events(request):
    event_bus = request.app.state.event_bus
    headers = {'Access-Control-Allow-Origin': 'http://localhost:5001'}
    return EventSourceResponse(event_bus.listen_for_events(), headers=headers)


def create_app():
    setup_logging()

    event_bus = EventBus()
    plugins = PluginManager(event_bus)

    routes = [
        Route("/", endpoint=homepage),
        Route("/events", endpoint=stream_events),
        Mount("/static", StaticFiles(directory="static", html=True), name="static"),
        *plugins.get_routes(),
    ]

    application = Starlette(
        debug=True,
        routes=routes,
        on_startup=[plugins.startup],
        on_shutdown=[plugins.shutdown, event_bus.shutdown],
    )
    application.state.event_bus = event_bus
    application.state.plugins = plugins

    return application


# The app object is created globally so that this module can run under an
# application server other than uvicorn, such as Gunicorn.
app = create_app()


def main():
    uvicorn.run(app, port=5000)


if __name__ == "__main__":
    main()
