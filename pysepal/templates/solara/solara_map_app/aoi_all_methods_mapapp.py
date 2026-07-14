"""AOI All Methods with MapApp Template.

Demonstrates all AOI selection methods using the MapApp layout with sidebar
steps and the centralized notification system.

To run:

```bash
pysepal$ ./run_solara.sh pysepal/templates/solara/solara_map_app/aoi_all_methods_mapapp.py --port 8901
```
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path

import ee
import solara

from pysepal import mapping as sm
from pysepal.sepalwidgets.vue_app import MapApp
from pysepal.solara import (
    get_current_gee_interface,
    get_current_theme_state,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)
from pysepal.solara.components.aoi import AoiView
from pysepal.solara.components.export import (
    ExportKind,
    ExportLauncher,
    ExportSource,
    ResolvedExport,
)
from pysepal.solara.notifications import NotificationProvider, use_notifications

DUMMY_DATA_DIR = Path(__file__).resolve().parents[4] / "tests" / "data" / "aoi_manual"
DEMO_CONSTANT_LAYER_ID = "demo_constant_10"
DEMO_PIXEL_AREA_LAYER_ID = "demo_pixel_area"

setup_solara_server(extra_asset_locations=[])


@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management."""
    return setup_sessions()


@dataclass(frozen=True, slots=True)
class DemoExportDataset:
    """Exportable demo dataset produced by the processing example."""

    id: str
    label: str
    kind: ExportKind
    ee_object: object
    description: str
    default_name: str
    region: object = None
    default_scale: int | None = None


def _get_aoi_key(aoi_value) -> str:
    """Return a stable key for the current AOI selection."""
    if aoi_value is None:
        return ""

    return f"{aoi_value.method}:{aoi_value.name}"


def _build_demo_datasets(aoi_value) -> tuple[DemoExportDataset, ...]:
    """Build demo exportable EE objects derived from the selected AOI."""
    if aoi_value is None or aoi_value.feature_collection is None:
        return ()

    region = aoi_value.feature_collection.geometry()
    name_prefix = aoi_value.name.replace(" ", "_")

    constant_image = ee.Image.constant(10).rename("constant_10").clip(region)
    pixel_area_image = ee.Image.pixelArea().rename("pixel_area_m2").clip(region)

    return (
        DemoExportDataset(
            id=DEMO_CONSTANT_LAYER_ID,
            label="Constant image (10) clipped to AOI",
            kind="image",
            ee_object=constant_image,
            description=(
                "Demo processing output created with ee.Image.constant(10).clip(aoi). "
                "This appears in the export dialog because the page registers it as an export source."
            ),
            default_name=f"{name_prefix}_constant_10",
            region=region,
            default_scale=30,
        ),
        DemoExportDataset(
            id=DEMO_PIXEL_AREA_LAYER_ID,
            label="Pixel area image clipped to AOI",
            kind="image",
            ee_object=pixel_area_image,
            description=(
                "Second derived image output produced by the processing demo to validate "
                "multiple exportable datasets in one dialog."
            ),
            default_name=f"{name_prefix}_pixel_area",
            region=region,
            default_scale=30,
        ),
    )


def _build_export_sources(
    aoi_value,
    processed_datasets: tuple[DemoExportDataset, ...],
) -> list[ExportSource]:
    """Create export sources from the AOI and any processed demo datasets."""
    sources: list[ExportSource] = []

    if aoi_value is not None and aoi_value.feature_collection is not None:
        sources.append(
            ExportSource(
                id="selected_aoi",
                label="Selected AOI boundary",
                kind="table",
                description="The AOI feature collection currently selected in the sidebar.",
                resolve=lambda aoi_value=aoi_value: ResolvedExport(
                    ee_object=aoi_value.feature_collection,
                    default_name=aoi_value.name,
                    drive_folder="pysepal_exports",
                    sepal_folder="exports",
                ),
            )
        )

    for dataset in processed_datasets:
        sources.append(
            ExportSource(
                id=dataset.id,
                label=dataset.label,
                kind=dataset.kind,
                description=dataset.description,
                resolve=lambda dataset=dataset: ResolvedExport(
                    ee_object=dataset.ee_object,
                    default_name=dataset.default_name,
                    region=dataset.region,
                    default_scale=dataset.default_scale,
                    drive_folder="pysepal_exports",
                    sepal_folder="exports",
                ),
            )
        )

    return sources


@solara.component
def AoiResultPanel(aoi_data, aoi_loading, is_pinned):
    """Right panel content showing AOI result details."""
    with solara.Column(style="gap: 8px;"):
        solara.Info(f"Sidebar pinned (Python-side): {is_pinned.value}")

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
                block=True,
            )
        else:
            solara.Info("No AOI selected yet. Use the sidebar to select one.")


@solara.component
def ProcessStep(aoi_data, processed_datasets, sepal_map):
    """Processing demo that also publishes exportable derived EE datasets."""
    notifications = use_notifications()

    async def run_process():
        if aoi_data.value is None or aoi_data.value.feature_collection is None:
            raise ValueError("Select an AOI first before running processing.")

        aoi_value = aoi_data.value
        demo_datasets = _build_demo_datasets(aoi_value)

        with notifications.track("Processing data", total_steps=5) as task:
            task.step("Loading AOI data...")
            await asyncio.sleep(1)
            task.set_progress(0.2)

            task.step("Building demo Earth Engine outputs...")
            await asyncio.sleep(1)
            task.set_progress(0.4)

            task.step("Adding derived layers to the map...")
            await sepal_map.add_ee_layer_async(
                demo_datasets[0].ee_object,
                vis_params={"min": 0, "max": 20, "palette": ["#f7fcf0", "#238b45"]},
                name=demo_datasets[0].label,
                key=demo_datasets[0].id,
            )
            await sepal_map.add_ee_layer_async(
                demo_datasets[1].ee_object,
                vis_params={"min": 0, "max": 5000, "palette": ["#fff7bc", "#d95f0e"]},
                name=demo_datasets[1].label,
                key=demo_datasets[1].id,
            )
            task.set_progress(0.7)

            task.step("Registering exportable datasets...")
            await asyncio.sleep(0.5)
            task.set_progress(0.85)

            task.step("Finalizing...")
            await asyncio.sleep(0.5)

        notifications.success(
            "Processing complete. Two derived EE images were added to the map and export list."
        )
        return demo_datasets

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
        prefer_threaded=False,
    )
    failing_task = solara.lab.use_task(
        run_failing_process,
        dependencies=None,
        raise_error=False,
        prefer_threaded=False,
    )

    def start_process():
        processed_datasets.set(())
        process_task()

    def _sync_processed_results() -> None:
        if process_task.finished and process_task.value is not None:
            processed_datasets.set(tuple(process_task.value))

    solara.use_effect(
        _sync_processed_results,
        [process_task.finished, process_task.value],
    )

    with solara.Column(style="gap: 12px;"):
        solara.Markdown("### Process AOI Data")

        if aoi_data.value:
            solara.Info(f"AOI ready: {aoi_data.value.name} ({aoi_data.value.method})")
            solara.Info(
                "Run Processing to create demo derived images, including "
                "`ee.Image.constant(10).clip(aoi)`, and register them in the export dialog."
            )
            solara.Button(
                "Run Processing",
                on_click=start_process,
                color="primary",
                loading=process_task.pending,
                disabled=process_task.pending,
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
        else:
            solara.Warning("Select an AOI first in the right panel.")


@solara.component
def AoiExportPanel(aoi_data, processed_datasets):
    """Export the selected AOI plus any processed demo datasets."""
    sources = _build_export_sources(aoi_data.value, processed_datasets.value)
    dataset_labels = [source.label for source in sources]

    with solara.Column(style="gap: 8px;"):
        ExportLauncher(
            sources=sources,
            dialog_title="Export datasets",
            default_target="gee",
            button_text=True,
            block=True,
        )

        if not aoi_data.value:
            solara.Info("Select an AOI first to enable export.")
        elif aoi_data.value.feature_collection is None:
            solara.Warning("This AOI does not expose an Earth Engine object to export.")
        elif not processed_datasets.value:
            solara.Info(
                "Run Processing to add demo image datasets. The export dialog only lists "
                "datasets that the page explicitly registers as export sources."
            )

        if dataset_labels:
            solara.Markdown(
                "**Available datasets**\n" + "\n".join(f"- {label}" for label in dataset_labels)
            )


@solara.component
def AoiAllMethodsMapApp():
    """All AOI methods demo using MapApp layout with notifications."""
    setup_theme_colors()

    gee_interface = get_current_gee_interface()
    theme_state = get_current_theme_state()

    # Shared AOI state
    aoi_data = solara.use_reactive(None)
    aoi_loading = solara.use_reactive(False)
    processed_datasets = solara.use_reactive(())
    is_pinned = solara.use_reactive(True)

    # Build map once
    def build_map():
        return sm.SepalMap(
            zoom=2,
            center=[0, 0],
            gee=True,
            gee_interface=gee_interface,
            fullscreen=True,
            theme_state=theme_state,
        )

    sepal_map = solara.use_memo(build_map, [id(gee_interface)])
    current_aoi_key = _get_aoi_key(aoi_data.value)
    previous_aoi_key_ref = solara.use_ref(current_aoi_key)

    def _clear_processed_outputs_on_aoi_change() -> None:
        previous_key = previous_aoi_key_ref.current
        if previous_key == current_aoi_key:
            return

        for dataset in processed_datasets.value:
            if dataset.kind == "image":
                sepal_map.remove_layer(dataset.id, none_ok=True)

        processed_datasets.set(())
        previous_aoi_key_ref.current = current_aoi_key

    solara.use_effect(_clear_processed_outputs_on_aoi_change, [current_aoi_key])

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
            "content": [
                AoiResultPanel(
                    aoi_data=aoi_data,
                    aoi_loading=aoi_loading,
                    is_pinned=is_pinned,
                )
            ],
        },
    ]

    right_panel_content = [
        *right_panel_content,
        {
            "title": "Export",
            "icon": "mdi-export-variant",
            "content": [
                AoiExportPanel(
                    aoi_data=aoi_data,
                    processed_datasets=processed_datasets,
                )
            ],
        },
        {
            "title": "Process",
            "icon": "mdi-cog-outline",
            "content": [
                ProcessStep(
                    aoi_data=aoi_data,
                    processed_datasets=processed_datasets,
                    sepal_map=sepal_map,
                )
            ],
            "divider": True,
        },
    ]

    # Notification system (toasts top-right, pill tracks map bottom-right)
    NotificationProvider()

    def _on_pin_change(value):
        is_pinned.set(value)
        print(f"[aoi_all_methods_mapapp] is_pinned -> {value}")

    MapApp.element(
        app_title="AOI All Methods",
        app_icon="mdi-map-marker-check",
        main_map=[sepal_map],
        steps_data=[],
        right_panel_config=right_panel_config,
        right_panel_content=right_panel_content,
        right_panel_open=True,
        theme_state=theme_state,
        on_is_pinned=_on_pin_change,
    )


@solara.component
@with_sepal_sessions(module_name="aoi_all_methods")
def Page():
    """Authenticated Solara-server entrypoint for the AOI methods demo."""
    AoiAllMethodsMapApp()
