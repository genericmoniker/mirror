"""
Entrypoint for configuring a mirror and any discovered plugins.
"""
from plugin_context import PluginContext
from plugin_discovery import discover_plugins


def main():
    # TODO: Get from the command line (or configure everything if none specified):
    name = "calendar"

    plugins = discover_plugins()
    module = plugins[name]
    module.configure_plugin(PluginContext(name).db)


if __name__ == "__main__":
    main()
