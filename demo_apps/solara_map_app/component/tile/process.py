"""Right-panel section that runs the demo processing."""

import asyncio

import solara
from component.model import LayerLegend
from component.parameter import (
    ELEVATION_CLASS_LAYER_ID,
    ELEVATION_CLASSES,
    PIXEL_AREA_LAYER_ID,
    PIXEL_AREA_VIS,
)
from component.scripts import (
    build_outputs,
    elevation_class_legend,
    gradient_legend,
    upsert_legends,
)

from pysepal.solara.notifications import use_notifications


@solara.component
def ProcessPanel(aoi_data, outputs, layer_legends, sepal_map, gee_interface):
    """Run the demo processing, add its layers and publish their legends."""
    notifications = use_notifications()

    async def run_process():
        if aoi_data.value is None or aoi_data.value.feature_collection is None:
            raise ValueError("Select an AOI first before running processing.")

        built = build_outputs(aoi_data.value)

        with notifications.track("Processing data", total_steps=4) as task:
            task.step("Building Earth Engine outputs...")
            await asyncio.sleep(0.5)
            task.set_progress(0.2)

            task.step("Adding derived layers to the map...")
            await sepal_map.add_ee_layer_async(
                built.pixel_area,
                vis_params=PIXEL_AREA_VIS,
                name="Pixel area (m²)",
                key=PIXEL_AREA_LAYER_ID,
            )
            await sepal_map.add_ee_layer_async(
                built.elevation_class,
                vis_params={
                    "min": 1,
                    "max": len(ELEVATION_CLASSES),
                    "palette": [color for _, _, color in ELEVATION_CLASSES],
                },
                name="Elevation classes",
                key=ELEVATION_CLASS_LAYER_ID,
            )
            task.set_progress(0.6)

            task.step("Measuring class areas...")
            class_legend = await elevation_class_legend(gee_interface, built)
            task.set_progress(0.9)

            task.step("Publishing legends and export sources...")
            layer_legends.set(
                upsert_legends(
                    layer_legends.value,
                    LayerLegend(
                        PIXEL_AREA_LAYER_ID,
                        "Pixel area (m²)",
                        gradient_legend("Pixel area (m²)", PIXEL_AREA_VIS),
                    ),
                    LayerLegend(ELEVATION_CLASS_LAYER_ID, "Elevation classes", class_legend),
                )
            )
            outputs.set(built)

        notifications.success("Processing complete. Pick a layer in the map legend to inspect it.")

    async def run_failing_process():
        """Simulate a Python exception mid-task to exercise error handling."""
        with notifications.track("Risky operation", total_steps=2) as task:
            task.step("Calling external service...")
            await asyncio.sleep(1)
            task.set_progress(0.5)

            task.step("Parsing response...")
            await asyncio.sleep(0.5)
            raise RuntimeError(
                "Simulated failure: external API returned malformed JSON at line 42."
            )

    process_task = solara.lab.use_task(
        run_process, dependencies=None, raise_error=False, prefer_threaded=False
    )
    failing_task = solara.lab.use_task(
        run_failing_process, dependencies=None, raise_error=False, prefer_threaded=False
    )

    has_aoi = aoi_data.value is not None and aoi_data.value.feature_collection is not None

    with solara.Column(style="gap: 8px;"):
        solara.Button(
            "Run Processing",
            on_click=process_task,
            color="primary",
            loading=process_task.pending,
            disabled=process_task.pending or not has_aoi,
            small=True,
            block=True,
        )
        solara.Button(
            "Simulate Error",
            on_click=failing_task,
            color="error",
            outlined=True,
            loading=failing_task.pending,
            disabled=failing_task.pending,
            small=True,
            block=True,
        )
