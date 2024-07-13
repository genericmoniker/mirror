"""Rotator helper functions."""

from mirror.plugin_manager import PluginManager


def render_rotator_widget(
    plugins: PluginManager,
    widgets: list[str],
    index: int,
    n: int,
) -> tuple[str, int, int]:
    """Render a rotator widget.

    Skips widgets that don't have any content to display.

    Returns (widget HTML, next index, next n).
    """
    for _ in range(len(widgets)):
        widget_name = widgets[index]
        html = plugins.render_widget(widget_name, n).strip()

        if index + 1 == len(widgets):
            next_index = 0
            next_n = n + 1  # Increment n whenever we loop through all widgets.
        else:
            next_index = index + 1
            next_n = n

        if html:
            return html, next_index, next_n

        index = next_index
        n = next_n

    # Nobody has anything to say...
    return "<!-- No content -->", next_index, next_n
