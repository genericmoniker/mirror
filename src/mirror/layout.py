"""Layout configuration for the mirror."""
import logging
import tomllib
from collections.abc import Iterable
from pathlib import Path

from mirror.plugin import Plugin
from mirror.plugin_manager import PluginManager

_logger = logging.getLogger(__name__)


class Layout:
    """Layout configuration for the mirror."""

    def __init__(self, config_file: Path, plugins: PluginManager) -> None:
        try:
            with config_file.open(mode="rb") as f:
                config = tomllib.load(f)
        except FileNotFoundError:
            _logger.warning("Layout configuration file not found: %s", config_file)
            config = {}
        widgets = config.get("widgets", {})
        left = widgets.get("left", [])
        right = widgets.get("right", [])
        bottom = widgets.get("bottom", [])
        self.left = self._valid_widgets(left, plugins)
        self.right = self._valid_widgets(right, plugins)
        self.bottom = self._valid_widgets(bottom, plugins)
        # TODO: If there are no widgets, use a default layout.

    @staticmethod
    def _valid_widgets(
        widgets: list[str],
        plugins: Iterable[Plugin],
    ) -> list[str]:
        valid_widgets = []
        for widget in widgets:
            plugin_name, _, widget_name = widget.partition(".")
            for plugin in plugins:
                if plugin.name == plugin_name:
                    # TODO: Check if widget_name is valid for plugin (template exists?)
                    valid_widgets.append(widget)
                    break
            else:
                _logger.warning("Ignoring widget for unknown plugin: %s", plugin_name)
        return valid_widgets
