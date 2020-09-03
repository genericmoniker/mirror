"""Package init.

The server-side parts of a plugin could be entirely implemented here, but to break up
the code into modules, we can instead just import the entrypoints for configuring and
creating the plugin.
"""
from .configure import configure_plugin
from .sample import create_plugin
from .sample import get_scripts
