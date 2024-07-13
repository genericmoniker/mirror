"""Plugin discovery module."""

import importlib
import pkgutil

import mirror.plugins
from mirror.plugin import Plugin


def discover_plugins() -> list[Plugin]:
    """Discover mirror plugins using the approach described in the URL below.

    https://packaging.python.org/guides/creating-and-discovering-plugins/#using-namespace-packages
    """
    namespace_package = mirror.plugins

    namespace_modules = pkgutil.iter_modules(
        namespace_package.__path__,
        namespace_package.__name__ + ".",
    )
    return [
        Plugin(name=name.split(".")[-1], module=importlib.import_module(name))
        for _, name, _ in namespace_modules
    ]
