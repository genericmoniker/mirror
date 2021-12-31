from mirror import oauth
from mirror.plugin_context import PluginDatabase


class PluginConfigureContext:
    """Services provided to plugins at configuration time.

    Plugins are provided with an instance of this class and do not create one
    themselves.
    """

    def __init__(self, plugin_name) -> None:
        self.db = PluginDatabase(plugin_name)
        self.oauth = oauth

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        self.db.close()
