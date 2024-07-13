"""TUI for configuring plugins."""

from textual.app import App, ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.widgets import Button, Checkbox, Input, Label

# Maybe we want a function like this?
# def config_dialog(title: str, form: ComposeResult):
#     pass


class ConfigApp(App):
    """TUI app for configuring plugins."""

    CSS_PATH = "config_tui.tcss"

    def compose(self) -> ComposeResult:
        form = Vertical(
            Label("Path to credentials.json to import:"),
            Input(),
            Label("Coming up regex filter:"),
            Input(),
            Checkbox("Re-request user permission"),
            id="form",
        )

        yield Vertical(
            Center(Label("Calendar Plugin Set Up"), id="title"),
            form,
            Horizontal(
                Button("OK", variant="primary"),
                Button("Cancel"),
                id="buttons",
            ),
            id="main",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.exit(str(event.button))
