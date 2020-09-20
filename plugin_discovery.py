import importlib
import pkgutil

import plugins


def discover_plugins():
    namespace_package = plugins

    namespace_modules = pkgutil.iter_modules(
        namespace_package.__path__, namespace_package.__name__ + "."
    )

    return {
        name.split(".")[-1]: importlib.import_module(name)
        for _, name, _ in namespace_modules
    }
