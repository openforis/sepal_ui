"""Solara FileInputComponent — canonical location.

Wraps the ipyvuetify FileInput widget in a Solara-native component.
"""

from pathlib import Path
from typing import Callable, List, Optional, Union

import solara

from pysepal.scripts.sepal_client import SepalClient
from pysepal.sepalwidgets.file_input import FileInput


@solara.component
def FileInputComponent(
    initial_folder: str = "",
    root: str = "",
    sepal_client: Optional[SepalClient] = None,
    extensions: List[str] = [],
    label: str = "Select a file",
    clearable: bool = True,
    value: Union[str, solara.Reactive[str]] = "",
    on_value: Optional[Callable[[str], None]] = None,
):
    """Solara component wrapper for FileInput widget.

    Args:
        initial_folder: The initial folder to read files from.
        root: Maximum root directory that can be accessed.
        sepal_client: Sepal client to access the server.
        extensions: List of file extensions to filter by.
        label: Label for the file selection button.
        clearable: Whether to show a clear button.
        value: Current selected file path (can be reactive).
        on_value: Callback function when value changes.

    Returns:
        FileInput element configured as a Solara component.
    """
    reactive_value = solara.use_reactive(value, on_value)
    del value, on_value

    is_syncing = solara.use_ref(False)

    root = root if root else "" if sepal_client else str(Path.home())

    file_input = FileInput.element(
        initial_folder=initial_folder,
        root=root,
        sepal_client=sepal_client,
        extensions=extensions,
        label=label,
        clearable=clearable,
        value=reactive_value.value,
        on_v_model=lambda v: None,
    )

    def setup_widget():
        real_widget = solara.get_widget(file_input)
        if real_widget is None:
            return

        if reactive_value.value and real_widget.v_model != reactive_value.value:
            real_widget.v_model = reactive_value.value

        def on_widget_change(change):
            if not is_syncing.current:
                is_syncing.current = True
                reactive_value.set(change["new"])
                is_syncing.current = False

        real_widget.observe(on_widget_change, "v_model")

        return lambda: real_widget.unobserve(on_widget_change, "v_model")

    solara.use_effect(setup_widget, [])

    def sync_to_widget():
        if is_syncing.current:
            return

        real_widget = solara.get_widget(file_input)
        if real_widget is None:
            return

        if real_widget.v_model != reactive_value.value:
            is_syncing.current = True
            real_widget.v_model = reactive_value.value
            is_syncing.current = False

    solara.use_effect(sync_to_widget, [reactive_value.value])

    return file_input
