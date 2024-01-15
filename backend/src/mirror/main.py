"""The main entry point for the backend server."""
import uvicorn
from sse_starlette.sse import EventSourceResponse
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from mirror.diagnostics import log_task_stacks
from mirror.event_bus import EventBus
from mirror.layout import Layout
from mirror.log import uvicorn_log_config
from mirror.paths import INSTANCE_DIR, ROOT_DIR
from mirror.plugin_manager import PluginManager


async def stream_events(request: Request) -> EventSourceResponse:
    event_bus = request.app.state.event_bus
    return EventSourceResponse(event_bus.listen_for_events())


async def diagnostics(request: Request) -> Response:  # noqa: ARG001
    log_task_stacks()
    return Response(status_code=204)


async def ready(request: Request) -> Response:  # noqa: ARG001
    return Response()


async def rotator(request: Request) -> Response:
    app = request.app
    context = build_template_context(request)
    return app.state.templates.TemplateResponse("rotator.html", context)


async def index(request: Request) -> Response:
    app = request.app
    context = build_template_context(request)
    return app.state.templates.TemplateResponse("index.html", context)


def build_template_context(request: Request, extra: dict | None = None) -> dict:
    extra = extra or {}
    app = request.app
    context = {
        "request": request,
        "plugins": app.state.plugins,
        "layout": app.state.layout,
    }
    context.update(extra)
    return context


def create_app() -> Starlette:
    event_bus = EventBus()
    plugins = PluginManager(event_bus)
    layout = Layout(INSTANCE_DIR / "mirror.toml", plugins)

    static_dir = ROOT_DIR / "backend" / "static"
    template_dir = [ROOT_DIR / "backend" / "templates"]

    plugin_static_mounts = [
        Mount(
            f"/plugin/{plugin.name}",
            StaticFiles(directory=plugin.static_path, html=True),
            name=plugin.name,
        )
        for plugin in plugins
        if plugin.static_path
    ]

    routes = [
        Route("/ready", endpoint=ready),
        Route("/rotator", endpoint=rotator),
        Route("/events", endpoint=stream_events),
        Route("/diag", endpoint=diagnostics),
        Mount("/static", StaticFiles(directory=static_dir, html=True), name="static"),
        Route("/", endpoint=index),
        *plugin_static_mounts,
    ]

    application = Starlette(
        debug=True,
        routes=routes,
        on_startup=[plugins.startup],
        on_shutdown=[plugins.shutdown, event_bus.shutdown],
    )
    application.state.layout = layout
    application.state.templates = Jinja2Templates(directory=template_dir)
    application.state.templates.env.globals["render_widget"] = plugins.render_widget
    application.state.event_bus = event_bus
    application.state.plugins = plugins

    return application


# The app object is created globally so that this module can run under an
# application server other than uvicorn, such as Gunicorn.
app = create_app()


def main() -> None:
    uvicorn.run(
        "mirror.main:app",
        host="0.0.0.0",  # noqa: S104
        port=5000,
        log_config=uvicorn_log_config(),
    )


if __name__ == "__main__":
    main()
