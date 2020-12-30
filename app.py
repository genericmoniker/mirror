import logging

from flask import Flask, render_template
from log import setup_logging
from plugin_context import PluginContext, start
from plugin_discovery import discover_plugins

_logger = logging.getLogger(__name__)


def create_app():
    """Application entrypoint.

    "flask run" looks for app.py and runs create_app (among other possibilities).
    """
    setup_logging()

    app = Flask(__name__, instance_relative_config=True)

    plugin_scripts = {}

    @app.route("/")
    def _index():
        return render_template("index.html", plugin_scripts=plugin_scripts)

    @app.route("/alive")
    def _alive():
        return "OK"

    start()
    _load_plugins(app, plugin_scripts)

    # TODO - Convert message stuff to plugins
    # ----------------------------------------------------------------------------------
    app.config.from_pyfile("config.py")

    import messages

    @app.before_first_request
    def _startup():
        messages.init_cache(app)

    @app.route("/message")
    def _message():
        return messages.get_message()

    # ----------------------------------------------------------------------------------

    return app


def _load_plugins(app: Flask, plugin_scripts: list) -> None:
    plugins = discover_plugins()
    loaded_plugins = [name for name in plugins.keys()]
    for name, module in plugins.items():
        try:
            blueprint = module.create_plugin(PluginContext(name))
            app.register_blueprint(blueprint, url_prefix="/" + name)
            plugin_scripts[name] = module.get_scripts()
        except Exception:
            _logger.exception("Failed to load plugin '%s'", name)
            loaded_plugins.remove(name)
    _logger.info("Loaded plugins: %s", ", ".join(loaded_plugins))
