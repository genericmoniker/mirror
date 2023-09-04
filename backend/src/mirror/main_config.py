"""Mirror configuration utility."""
import argparse

from mirror.plugin_configure_context import PluginConfigureContext
from mirror.plugin_discovery import discover_plugins


def main() -> None:
    plugins = discover_plugins()
    parser = argparse.ArgumentParser(
        description="Mirror configuration utility",
        epilog="Available plugins: " + ", ".join(plugins.keys()),
    )
    parser.add_argument("--plugins", nargs="*")
    args = parser.parse_args()

    # TODO: Set up file logging (since we're using stdout).

    plugins_to_configure = args.plugins or plugins.keys()

    for name in plugins_to_configure:
        module = plugins[name]
        if not hasattr(module, "configure_plugin"):
            continue
        with PluginConfigureContext(name) as context:
            module.configure_plugin(context)


if __name__ == "__main__":
    main()
