"""Plugin discovery module."""
import importlib
import pkgutil
from types import ModuleType

import mirror.plugins


def discover_plugins() -> dict[str, ModuleType]:
    """Discover mirror plugins using the approach described in the URL below.

    https://packaging.python.org/guides/creating-and-discovering-plugins/#using-namespace-packages
    """
    namespace_package = mirror.plugins

    namespace_modules = pkgutil.iter_modules(
        namespace_package.__path__,
        namespace_package.__name__ + ".",
    )

    return {
        name.split(".")[-1]: importlib.import_module(name)
        for _, name, _ in namespace_modules
    }
