"""Mirror configuration utility.

This program interactively prompts the user for plugin configuration and writes the
configuration to the database for the plugin to read at runtime.
"""
import argparse

from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_discovery import discover_plugins


def main() -> None:
    plugins = discover_plugins()
    parser = argparse.ArgumentParser(
        description="Mirror configuration utility",
        epilog="Available plugins: " + ", ".join(str(plugins)),
    )
    parser.add_argument("--plugins", nargs="*")
    args = parser.parse_args()

    # TODO: Set up file logging (since we're using stdout).

    plugins_to_configure = [p for p in plugins if p.name in args.plugins] or plugins

    for plugin in plugins_to_configure:
        if not hasattr(plugin.module, "configure_plugin"):
            continue
        with PluginConfigureContext(plugin.name) as context:
            plugin.module.configure_plugin(context)


if __name__ == "__main__":
    main()
