import uvicorn
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from mirror.event_bus import EventBus
from mirror.log import uvicorn_log_config
from mirror.paths import ROOTDIR
from mirror.plugin_manager import PluginManager


async def stream_events(request):
    event_bus = request.app.state.event_bus

    # Allow requests from the frontend dev server (npm run dev):
    headers = {"Access-Control-Allow-Origin": "http://localhost:5001"}

    return EventSourceResponse(event_bus.listen_for_events(), headers=headers)


def create_app():
    event_bus = EventBus()
    plugins = PluginManager(event_bus)
    static_dir = ROOTDIR / "frontend/public"

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
    uvicorn.run(app, host="0.0.0.0", port=5000, log_config=uvicorn_log_config())


if __name__ == "__main__":
    main()
