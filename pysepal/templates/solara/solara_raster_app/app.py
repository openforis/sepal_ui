"""Local raster rendering: continuous ramps, categorical class colors, big files.

Three buttons, one per path through :meth:`~pysepal.mapping.SepalMap.add_raster`:
a continuous colormap, exact per-class colors, and a raster large enough that
preparing it has to happen off the event loop.

Set ``PYSEPAL_DEMO_RASTER_DIR`` to a directory holding ``aa_test_congo.tif`` and
``hansen_bolivia.tif`` to run against real class maps; without it the demo
generates a small synthetic class raster so it still runs anywhere.

The UI lives in :func:`RasterAppDemo` so the same code serves both runtimes --
``Page`` is the Solara entrypoint and ``ui.ipynb`` is a thin Voila one.

To run:

```bash
pysepal$ ./run_solara.sh pysepal/templates/solara/solara_raster_app/app.py --port 8901
```
"""

import os
import tempfile
from pathlib import Path

import solara

import pysepal.sepalwidgets as sw
from pysepal import mapping as sm
from pysepal.sepalwidgets.vue_app import MapApp
from pysepal.solara import (
    get_current_theme_state,
    setup_solara_server,
    setup_theme_colors,
)
from pysepal.solara.components.task_button import TaskButtonComponent, use_task_button
from pysepal.solara.notifications import NotificationProvider, use_notifications

setup_solara_server(extra_asset_locations=[])

#: Points the demo at real class maps instead of the generated stand-in.
RASTER_DIR_ENV_VAR = "PYSEPAL_DEMO_RASTER_DIR"

# aa_test_congo holds these nine classes; codes 2 and 4 are the ones a continuous
# ramp stretched over 2-34 renders as good as black.
CONGO_COLORS = {
    2: "#8ecae6",
    4: "#219ebc",
    11: "#2d6a4f",
    12: "#40916c",
    13: "#95d5b2",
    31: "#e9c46a",
    32: "#f4a261",
    33: "#e76f51",
    34: "#9b2226",
}

# hansen loss year band: 0 is "no loss" and a real, sampleable class, not background
HANSEN_COLORS = {0: "#1b4332", 5: "#e63946"}


def _synthetic_raster(path: Path, codes: dict) -> Path:
    """Write a small class raster, so the demo runs without the real products."""
    import numpy as np
    import rasterio as rio
    from rasterio.transform import from_origin

    if path.exists():
        return path

    values = sorted(codes)
    size = 512
    data = np.zeros((size, size), dtype="int16")
    for band, value in enumerate(values):
        data[:, band * size // len(values) : (band + 1) * size // len(values)] = value

    path.parent.mkdir(parents=True, exist_ok=True)
    with rio.open(
        path,
        "w",
        driver="GTiff",
        height=size,
        width=size,
        count=1,
        dtype="int16",
        crs="EPSG:4326",
        transform=from_origin(20, 0, 0.01, 0.01),
    ) as dataset:
        dataset.write(data, 1)

    return path


def demo_rasters() -> dict:
    """Return the two rasters to draw, generating stand-ins when absent."""
    directory = os.environ.get(RASTER_DIR_ENV_VAR)
    if directory:
        congo = Path(directory) / "aa_test_congo.tif"
        hansen = Path(directory) / "hansen_bolivia.tif"
        if congo.is_file() and hansen.is_file():
            return {"congo": congo, "hansen": hansen, "synthetic": False}

    scratch = Path(tempfile.gettempdir()) / "pysepal-raster-demo"
    return {
        "congo": _synthetic_raster(scratch / "classes.tif", CONGO_COLORS),
        "hansen": _synthetic_raster(scratch / "loss.tif", HANSEN_COLORS),
        "synthetic": True,
    }


@solara.component
def RasterAppDemo():
    """Map plus a panel of buttons, one per raster-rendering path."""
    setup_theme_colors()
    theme_state = get_current_theme_state()
    notifications = use_notifications()

    rasters = solara.use_memo(demo_rasters, [])

    def build_map():
        return sm.SepalMap(
            zoom=3, center=[0, 0], gee=False, fullscreen=True, theme_state=theme_state
        )

    sepal_map = solara.use_memo(build_map, [])

    async def add_continuous():
        """What every raster looked like before class_colors: a stretched ramp."""
        with notifications.track("Continuous colormap") as task:
            task.step("preparing COG...")
            await sepal_map.add_raster_async(
                rasters["congo"],
                layer_name="Classes (continuous)",
                key="continuous",
                colormap="inferno",
            )
        notifications.success("Continuous ramp added")

    async def add_class_colors():
        """The same raster, each class in its own color."""
        with notifications.track("Class colors") as task:
            task.step("preparing COG...")
            await sepal_map.add_raster_async(
                rasters["congo"],
                layer_name="Classes (exact)",
                key="classes",
                class_colors=CONGO_COLORS,
            )
        notifications.success(f"{len(CONGO_COLORS)} classes added")

    async def add_large():
        """A raster with no overviews, which is the case ``optimize`` exists for."""
        with notifications.track("Large raster") as task:
            task.step("preparing COG with overviews...")
            await sepal_map.add_raster_async(
                rasters["hansen"],
                layer_name="Loss year",
                key="large",
                class_colors=HANSEN_COLORS,
            )
        notifications.success("Large raster added")

    continuous_task = solara.lab.use_task(
        add_continuous, dependencies=None, raise_error=False, prefer_threaded=False
    )
    classes_task = solara.lab.use_task(
        add_class_colors, dependencies=None, raise_error=False, prefer_threaded=False
    )
    large_task = solara.lab.use_task(
        add_large, dependencies=None, raise_error=False, prefer_threaded=False
    )

    continuous_props = use_task_button(continuous_task, on_start=continuous_task)
    classes_props = use_task_button(classes_task, on_start=classes_task)
    large_props = use_task_button(large_task, on_start=large_task)

    def build_clear_button():
        """A plain ipyvuetify button, handed to MapApp intact with its handler."""
        button = sw.Btn("clear rasters", small=True, block=True)

        def clear():
            for key in ("continuous", "classes", "large"):
                sepal_map.remove_layer(key, none_ok=True)

        button.on_event("click", lambda *args: clear())
        return button

    clear_button = solara.use_memo(build_clear_button, [id(sepal_map)])

    source = "generated stand-ins" if rasters["synthetic"] else "real class maps"

    # Toasts top-right, task progress pill bottom-right.
    NotificationProvider()

    MapApp.element(
        app_title="Local rasters",
        app_icon="mdi-layers",
        main_map=[sepal_map],
        steps_data=[],
        right_panel_config={
            "title": "Rasters",
            "icon": "mdi-image",
            "width": 380,
            "description": "Each button renders a local raster through a different path.",
        },
        right_panel_content=[
            {
                "title": "Local rasters",
                "icon": "mdi-image",
                "content": [
                    TaskButtonComponent(
                        label="continuous ramp", **continuous_props, small=True, block=True
                    ),
                    TaskButtonComponent(
                        label="class colors", **classes_props, small=True, block=True
                    ),
                    TaskButtonComponent(
                        label="large raster", **large_props, small=True, block=True
                    ),
                    clear_button,
                ],
                "description": (
                    f"Drawing {source}. A continuous ramp stretched across sparse class "
                    f"codes renders them near-black; class_colors draws each one exactly. "
                    f"Set {RASTER_DIR_ENV_VAR} to use real products."
                ),
            }
        ],
        right_panel_open=True,
        theme_state=theme_state,
        dialog_width=750,
    )


@solara.component
def Page():
    """Solara entrypoint -- no SEPAL session, the raster path is entirely local."""
    RasterAppDemo()
