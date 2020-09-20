"""
Entrypoint for configuring a mirror and any discovered plugins.
"""
import argparse

from plugin_context import PluginContext
from plugin_discovery import discover_plugins


def main():
    parser = argparse.ArgumentParser(description="Mirror configuration utility")
    parser.add_argument("--plugins", nargs="*")
    args = parser.parse_args()

    # TODO: Set up file logging (since we're using stdout).

    plugins = discover_plugins()
    plugins_to_configure = args.plugins or plugins.keys()

    for name in plugins_to_configure:
        module = plugins[name]
        context = PluginContext(name)
        try:
            module.configure_plugin(context.db)
        finally:
            context.close()


if __name__ == "__main__":
    main()
