"""Services provided to plugins at configuration time."""
from mirror import oauth
from mirror.plugin_context import PluginDatabase


class PluginConfigureContext:
    """Services provided to plugins at configuration time.

    Plugins are provided with an instance of this class and do not create one
    themselves.
    """

    def __init__(self, plugin_name: str) -> None:
        """Initialize the plugin context."""
        self.db = PluginDatabase(plugin_name)
        self.oauth = oauth

    def __enter__(self) -> "PluginConfigureContext":
        """Enter the context."""
        return self

    def __exit__(self, *args) -> None:
        """Exit the context."""
        self.close()

    def close(self) -> None:
        """Close the context."""
        self.db.close()
