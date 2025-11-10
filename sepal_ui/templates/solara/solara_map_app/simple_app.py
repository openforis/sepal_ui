"""Simple Solara application template for SEPAL UI.

This module provides a basic example of a Solara application with SEPAL UI integration,
demonstrating file input functionality and session management.
"""

import solara

from sepal_ui.sepalwidgets.file_input import FileInput
from sepal_ui.solara import (
    get_current_gee_interface,
    get_current_sepal_client,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)

setup_solara_server(extra_asset_locations=[])


@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management for Solara applications."""
    return setup_sessions()


@solara.component
@with_sepal_sessions(module_name="test")
def Page():
    """Main page component with file input widget."""
    setup_theme_colors()
    selected_file = solara.use_reactive("")

    get_current_gee_interface()
    sepal_client = get_current_sepal_client()

    FileInput.element(
        sepal_client=sepal_client,
    )

    if selected_file.value:
        solara.Markdown(f"**Selected:** {selected_file.value}")
