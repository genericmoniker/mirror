import argparse

from mirror.plugin_context import PluginDatabase
from mirror.plugin_discovery import discover_plugins


def main():
    parser = argparse.ArgumentParser(description="Mirror configuration utility")
    parser.add_argument("--plugins", nargs="*")
    args = parser.parse_args()

    # TODO: Set up file logging (since we're using stdout).

    plugins = discover_plugins()
    plugins_to_configure = args.plugins or plugins.keys()

    for name in plugins_to_configure:
        module = plugins[name]
        if not hasattr(module, "configure_plugin"):
            continue
        db = PluginDatabase(name)
        try:
            module.configure_plugin(db)
        finally:
            db.close()


if __name__ == "__main__":
    main()
