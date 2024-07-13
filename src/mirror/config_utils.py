"""Utilities for plugin configuration."""

from dataclasses import dataclass
from typing import Any

from prompt_toolkit.application import Application
from prompt_toolkit.application.current import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import Completer
from prompt_toolkit.filters import FilterOrBool
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import AnyContainer, HSplit
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import BaseStyle
from prompt_toolkit.validation import Validator
from prompt_toolkit.widgets import (
    Button,
    Checkbox,
    Dialog,
    Label,
    TextArea,
    ValidationToolbar,
)


@dataclass
class Input:
    """An input field for a configuration dialog.

    Note: Validation is not fully baked. It only triggers when hitting "Enter" within
    the input field. It does not prevent the dialog from closing when clicking "OK".
    The ValidationToolbar needs to be enhanced to work with more than just the current
    buffer, too, which is hinted at here:
    https://github.com/prompt-toolkit/python-prompt-toolkit/issues/1715
    """

    name: str
    text: AnyFormattedText = ""
    default: str = ""
    completer: Completer | None = None
    validator: Validator | None = None
    password: FilterOrBool = False


def create_dialog(
    title: AnyFormattedText = "",
    ok_text: str = "OK",
    cancel_text: str = "Cancel",
    inputs: list[Input] | None = None,
    style: BaseStyle | None = None,
) -> Application[str]:
    """Display a configuration dialog.

    Return a map of input name to entered text, or None when cancelled.

    Based on the dialogs in:
    https://github.com/prompt-toolkit/python-prompt-toolkit/blob/master/src/prompt_toolkit/shortcuts/dialogs.py
    """
    inputs = inputs or []

    def accept(buf: Buffer) -> bool:  # noqa: ARG001 (unused-function-argument)
        get_app().layout.focus(ok_button)
        return True  # Keep text.

    def ok_handler() -> None:
        result = {i.name: input_map[i.name].text for i in inputs}
        get_app().exit(result=result)

    def cancel_handler() -> None:
        get_app().exit()

    ok_button = Button(text=ok_text, handler=ok_handler)
    cancel_button = Button(text=cancel_text, handler=cancel_handler)

    input_map = {i.name: i for i in inputs}
    controls = []
    for i in inputs:
        label = Label(text=i.text)
        controls.append(label)
        text_area = TextArea(
            text=i.default,
            multiline=False,
            password=i.password,
            completer=i.completer,
            validator=i.validator,
            accept_handler=accept,
        )
        controls.append(text_area)
        input_map[i.name] = text_area
    controls.append(Checkbox("A checkbox"))
    controls.append(ValidationToolbar())

    dialog = Dialog(
        title=title,
        body=HSplit(
            controls,
            padding=Dimension(preferred=1, max=1),
        ),
        buttons=[ok_button, cancel_button],
        with_background=True,
    )

    return _create_app(dialog, style)


def _create_app(dialog: AnyContainer, style: BaseStyle | None) -> Application[Any]:
    # Key bindings.
    bindings = KeyBindings()
    bindings.add("tab")(focus_next)
    bindings.add("s-tab")(focus_previous)

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=True,
    )


# Example usage.
if __name__ == "__main__":

    def email_validator(text: str) -> bool:
        return "@" in text

    validator = Validator.from_callable(
        email_validator,
        error_message="Invalid email address.",
    )

    inputs = [
        Input(name="name", text="Name:", default="John Doe"),
        Input(name="email", text="Email:", validator=validator),
        Input(name="password", text="Password:", password=True),
    ]
    dialog = create_dialog(title="Plugin Set Up", inputs=inputs)
    result = dialog.run()
    print(result)
