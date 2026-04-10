"""AOI All Methods with MapApp Template.

Demonstrates all AOI selection methods using the MapApp layout with sidebar
steps and the centralized notification system.

To run:

```bash
pysepal$ ./run_solara.sh pysepal/templates/solara/solara_map_app/aoi_all_methods_mapapp.py --port 8901
```
"""

import asyncio
from pathlib import Path

import solara
from solara.lab.components.theming import theme

from pysepal import mapping as sm
from pysepal.sepalwidgets.vue_app import MapApp, ThemeToggle
from pysepal.solara import (
    get_current_gee_interface,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)
from pysepal.solara.components.aoi import AoiView
from pysepal.solara.notifications import NotificationProvider, use_notifications

DUMMY_DATA_DIR = Path(__file__).resolve().parents[4] / "tests" / "data" / "aoi_manual"

setup_solara_server(extra_asset_locations=[])


@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management."""
    return setup_sessions()


@solara.component
def AoiResultPanel(aoi_data, aoi_loading):
    """Right panel content showing AOI result details."""
    if aoi_loading.value:
        solara.ProgressLinear(True)
        solara.Info("Processing...")

    if aoi_data.value:
        with solara.Column(style="gap: 4px;"):
            solara.Text(f"Method: {aoi_data.value.method}")
            solara.Text(f"Name: {aoi_data.value.name}")
            solara.Text(f"GEE: {aoi_data.value.gee}")
            solara.Text(f"Has GDF: {aoi_data.value.gdf is not None}")
            solara.Text(f"Has EE object: {aoi_data.value.feature_collection is not None}")
            if aoi_data.value.gdf is not None:
                solara.Text(f"Features: {len(aoi_data.value.gdf)}")
                solara.Text(
                    f"Columns: {', '.join(c for c in aoi_data.value.gdf.columns if c != 'geometry')}"
                )

        solara.Button(
            "Clear AOI",
            on_click=lambda: aoi_data.set(None),
            color="error",
            outlined=True,
            small=True,
        )
    else:
        solara.Info("No AOI selected yet. Use the sidebar to select one.")


@solara.component
def ProcessStep(aoi_data):
    """Dummy processing step to demonstrate task tracking in the notification pill."""
    notifications = use_notifications()

    async def run_process():
        with notifications.track("Processing data", total_steps=4) as task:
            task.step("Loading AOI data...")
            await asyncio.sleep(2)
            task.set_progress(0.25)

            task.step("Computing statistics...")
            await asyncio.sleep(3)
            task.set_progress(0.5)

            task.step("Generating report...")
            await asyncio.sleep(2)
            task.set_progress(0.75)

            task.step("Finalizing...")
            await asyncio.sleep(1)

        notifications.success("Processing complete!")

    async def run_failing_process():
        """Simulate a Python exception mid-task to test error handling."""
        with notifications.track("Risky operation", total_steps=3) as task:
            task.step("Preparing data...")
            await asyncio.sleep(1)
            task.set_progress(0.3)

            task.step("Calling external service...")
            await asyncio.sleep(1)
            task.set_progress(0.6)

            task.step("Parsing response...")
            await asyncio.sleep(0.5)
            # Simulate a real error
            raise RuntimeError(
                "Simulated failure: external API returned malformed JSON "
                "at line 42. Check the server logs for details."
            )

    process_task = solara.lab.use_task(
        run_process,
        dependencies=None,
        raise_error=False,
    )
    failing_task = solara.lab.use_task(
        run_failing_process,
        dependencies=None,
        raise_error=False,
    )

    with solara.Column(style="gap: 12px;"):
        solara.Markdown("### Process AOI Data")

        if aoi_data.value:
            solara.Info(f"AOI ready: {aoi_data.value.name} ({aoi_data.value.method})")
            solara.Button(
                "Run Processing",
                on_click=process_task,
                color="primary",
                loading=process_task.pending,
                disabled=process_task.pending,
                block=True,
            )
            solara.Button(
                "Simulate Error",
                on_click=failing_task,
                color="error",
                outlined=True,
                loading=failing_task.pending,
                disabled=failing_task.pending,
                block=True,
            )
        else:
            solara.Warning("Select an AOI first in the right panel.")


@solara.component
@with_sepal_sessions(module_name="aoi_all_methods")
def Page():
    """All AOI methods demo using MapApp layout with notifications."""
    setup_theme_colors()

    theme_toggle = ThemeToggle()
    theme_toggle.observe(lambda e: setattr(theme, "dark", e["new"]), "dark")

    gee_interface = get_current_gee_interface()

    # Shared AOI state
    aoi_data = solara.use_reactive(None)
    aoi_loading = solara.use_reactive(False)

    # Build map once
    def build_map():
        return sm.SepalMap(
            zoom=2,
            center=[0, 0],
            gee=True,
            gee_interface=gee_interface,
            fullscreen=True,
            theme_toggle=theme_toggle,
        )

    sepal_map = solara.use_memo(build_map, [id(gee_interface)])

    # AoiView goes in the right panel
    aoi_view = AoiView(
        value=aoi_data,
        loading=aoi_loading,
        methods="ALL",
        map_=sepal_map,
        gee=True,
        file_initial_folder=str(DUMMY_DATA_DIR),
    )

    right_panel_config = {
        "title": "Select AOI",
        "icon": "mdi-map-marker-check",
        "width": 400,
        "description": "Choose an AOI method and selection.",
    }

    right_panel_content = [
        {
            "title": "AOI Selection",
            "icon": "mdi-map-marker-check",
            "content": [aoi_view],
        },
        {
            "title": "Result",
            "icon": "mdi-information-outline",
            "content": [AoiResultPanel(aoi_data=aoi_data, aoi_loading=aoi_loading)],
        },
    ]

    right_panel_content = [
        *right_panel_content,
        {
            "title": "Process",
            "icon": "mdi-cog-outline",
            "content": [ProcessStep(aoi_data=aoi_data)],
            "divider": True,
        },
    ]

    # Notification system (toasts top-right, pill tracks map bottom-right)
    NotificationProvider()

    MapApp.element(
        app_title="AOI All Methods",
        app_icon="mdi-map-marker-check",
        main_map=[sepal_map],
        steps_data=[],
        right_panel_config=right_panel_config,
        right_panel_content=right_panel_content,
        right_panel_open=True,
        theme_toggle=[theme_toggle],
    )
