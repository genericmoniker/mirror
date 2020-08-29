import logging

from flask import Flask, jsonify, render_template

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

    @app.route("/")
    def _root():
        return render_template("index.html")

    @app.route("/alive")
    def _alive():
        return "OK"

    @app.route("/discovery")
    def _discovery():
        return jsonify({})

    start()
    _load_plugins(app)

    return app


def _load_plugins(app: Flask) -> None:
    plugins = discover_plugins()
    for name, module in plugins.items():
        try:
            blueprint = module.create_plugin(PluginContext(name))
            app.register_blueprint(blueprint, url_prefix='/' + name)
        except Exception:
            _logger.exception("Failed to load plugin '%s'", name)
