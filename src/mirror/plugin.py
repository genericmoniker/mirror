"""Plugin definition module."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types import ModuleType

    from mirror.plugin_context import PluginContext

from jinja2 import Environment, FileSystemLoader


class Plugin:
    """A plugin that provides content to the mirror.

    This is the interface that the application uses to interact with plugins and is
    instantiated automatically when a plugin is discovered.
    """

    def __init__(self, name: str, module: ModuleType) -> None:
        """Initialize the plugin."""
        self.name = name
        self.module = module

        # Set up the template rendering environment.
        self.widget_contexts: dict[str, dict] = {}

        def url_for(filename: str) -> str:
            """Generate a URL for a plugin's static asset."""
            return f"/plugin/{self.name}/{filename}"

        # Note: leaving autoescape=False (the default) so that the widget() macro can
        # return HTML markup (otherwise it will be escaped). Thus ignoring S701.
        self.env = Environment(loader=FileSystemLoader(self.path))  # noqa: S701

        # Widget templates can use the `url_for` function.
        self.env.globals["url_for"] = url_for

    def __str__(self) -> str:
        return self.name

    async def set_authorization_code(
        self,
        plugin_context: PluginContext,
        code: str,
        state: str,
    ) -> None:
        """Set the authorization code for the plugin.

        This is typically called after the user has authorized the plugin and the
        authorization code has been received.
        """
        if hasattr(self.module, "set_authorization_code"):
            await self.module.set_authorization_code(plugin_context, code, state)

    def startup(self, plugin_context: PluginContext) -> None:
        """Start the plugin."""
        if hasattr(self.module, "start_plugin"):
            self.module.start_plugin(plugin_context)

    def shutdown(self, plugin_context: PluginContext) -> None:
        """Stop the plugin."""
        if hasattr(self.module, "stop_plugin"):
            self.module.stop_plugin(plugin_context)

    def render(
        self,
        context: dict | None,
        widget: str | None,
        n: int | None = None,
    ) -> str:
        """Render a plugin's widget template.

        `context` is passed to the widget template. If `context` is None, the context
        from the previous call to `render()` is used. If there is no previous context,
        an empty context is used.

        `widget` is the name of the widget to render. If `widget` is not specified, the
        plugin's main template (<plugin_name>.html) is rendered.

        `n` is the number of times the widget has been rendered. This is useful for
        widgets that need to maintain state across multiple renderings.
        """
        widget = widget or self.name
        if context is None:
            context = self.widget_contexts.get(widget, {})
        context["n"] = n
        self.widget_contexts[widget] = copy.deepcopy(context)
        template_name = f"{widget}.html"
        template = self.env.get_template(template_name)
        rendered_widget = template.render(**context)
        return rendered_widget

    @property
    def path(self) -> Path:
        """The plugin's root directory."""
        return Path(self.module.__path__[0])

    @property
    def static_path(self) -> Path | None:
        """The plugin's static assets directory.

        Returns None if the plugin does not have a static directory.
        """
        p = self.path / "static"
        return p if p.exists() else None

    @property
    def scripts(self) -> list[str]:
        """The plugin's script filenames.

        The filenames are relative to the plugin's static directory.
        """
        if not self.static_path:
            return []
        return [p.name for p in self.static_path.glob("*.js")]

    @property
    def stylesheets(self) -> list[str]:
        """The plugin's stylesheet filenames.

        The filenames are relative to the plugin's static directory.
        """
        if not self.static_path:
            return []
        return [p.name for p in self.static_path.glob("*.css")]
