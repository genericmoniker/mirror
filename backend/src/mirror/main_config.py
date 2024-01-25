"""Mirror configuration utility.

This program interactively prompts the user for plugin configuration and writes the
configuration to the database for the plugin to read at runtime.
"""
import argparse

from mirror.plugin import Plugin
from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_discovery import discover_plugins


def main() -> None:
    plugins = discover_plugins()
    plugin_names = [plugin.name for plugin in plugins]
    available = "Available plugins: " + ", ".join(plugin_names)
    parser = argparse.ArgumentParser(
        description="Mirror configuration utility",
        epilog=available,
    )
    parser.add_argument("--plugins", nargs="*")
    args = parser.parse_args()

    # TODO: Set up file logging (since we're using stdout).

    for plugin_name in args.plugins or []:
        if plugin_name not in plugin_names:
            print(f"Unknown plugin: {plugin_name}")
            print(available)
            return

    configure(plugins, args.plugins)


def configure(plugins: list[Plugin], plugin_names: list[str]) -> None:
    """Configure plugins.

    If `plugin_names` is specified, only those plugins are configured. Otherwise, all
    plugins are configured.
    """
    try:
        plugins_to_configure = [p for p in plugins if p.name in plugin_names] or plugins

        for plugin in plugins_to_configure:
            if not hasattr(plugin.module, "configure_plugin"):
                continue
            with PluginConfigureContext(plugin.name) as context:
                plugin.module.configure_plugin(context)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
