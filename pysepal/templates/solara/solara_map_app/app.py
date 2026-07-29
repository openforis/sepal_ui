"""SEPAL Solara map application template.

One app exercising what a real SEPAL module needs: AOI selection, async
processing with progress notifications, layer management, a floating map legend
driven by the layers currently on the map, and Earth Engine / Drive / SEPAL
exports.

The UI lives in :func:`MapAppDemo` so the same code serves both runtimes --
``Page`` wraps it with SEPAL session auth for Solara, and ``ui.ipynb`` is a thin
Voila entrypoint that displays it directly.

To run:

```bash
pysepal$ ./run_solara.sh pysepal/templates/solara/solara_map_app/app.py --port 8901
```
"""

import asyncio
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

import ee
import solara
from component.model import AppModel
from ipyleaflet import PMTilesLayer

import pysepal.sepalwidgets as sw
from pysepal import mapping as sm
from pysepal.sepalwidgets.vue_app import MapApp
from pysepal.solara import (
    get_current_drive_interface,
    get_current_gee_interface,
    get_current_theme_state,
    setup_sessions,
    setup_solara_server,
    setup_theme_colors,
    with_sepal_sessions,
)
from pysepal.solara.components.admin import AdminButton
from pysepal.solara.components.aoi import AoiView
from pysepal.solara.components.export import (
    ExportLauncher,
    ExportSource,
    ResolvedExport,
)
from pysepal.solara.components.legend import (
    DiscreteEntry,
    GradientEntry,
    LegendComponent,
    LegendData,
)
from pysepal.solara.components.task_button import TaskButtonComponent, use_task_button
from pysepal.solara.notifications import NotificationProvider, use_notifications

logger = logging.getLogger("SEPALUI.map_app")

DUMMY_DATA_DIR = Path(__file__).resolve().parents[4] / "tests" / "data" / "aoi_manual"

NDVI_LAYER_ID = "demo_ndvi"
PIXEL_AREA_LAYER_ID = "demo_pixel_area"
ELEVATION_CLASS_LAYER_ID = "demo_elevation_class"
PMTILES_LAYER_ID = "demo_pmtiles"
AOI_LAYER_IDS = (PIXEL_AREA_LAYER_ID, ELEVATION_CLASS_LAYER_ID)

DEMO_CENTER = [4.75, -74.12]
NDVI_VIS = {"min": -0.2, "max": 0.9, "palette": ["#d7191c", "#ffffbf", "#1a9641"]}
PIXEL_AREA_VIS = {"min": 0, "max": 5000, "palette": ["#fff7bc", "#d95f0e"]}

# (pixel value, legend label, color) -- drives the EE reclassification, the map
# palette and the legend chips from a single source.
ELEVATION_CLASSES = (
    (1, "Lowland (< 500 m)", "#c7e9b4"),
    (2, "Upland (500-1500 m)", "#41b6c4"),
    (3, "Highland (>= 1500 m)", "#253494"),
)

# Vector tiles read straight from a public archive: the browser range-requests the
# PMTiles itself, so nothing is proxied through the kernel. ``source-layer`` must
# match a layer id inside the archive ("buildings" here) or nothing is painted.
PMTILES_URL = "https://r2-public.protomaps.com/protomaps-sample-datasets/nz-buildings-v3.pmtiles"
PMTILES_CENTER = [-43.5565, 172.6062]
PMTILES_STYLE = {
    "version": 8,
    "sources": {"nz_buildings": {"type": "vector", "url": f"pmtiles://{PMTILES_URL}"}},
    "layers": [
        {
            "id": "buildings-fill",
            "type": "fill",
            "source": "nz_buildings",
            "source-layer": "buildings",
            "paint": {"fill-color": "#41b6c4", "fill-opacity": 0.6},
        },
        {
            "id": "buildings-outline",
            "type": "line",
            "source": "nz_buildings",
            "source-layer": "buildings",
            "paint": {"line-color": "#253494", "line-width": 0.5},
        },
    ],
}

setup_solara_server(extra_asset_locations=[])


@solara.lab.on_kernel_start
def on_kernel_start():
    """Set up sessions management."""
    return setup_sessions()


@dataclass(frozen=True, slots=True)
class ProcessingOutputs:
    """Earth Engine objects produced by one processing run."""

    pixel_area: ee.Image
    elevation_class: ee.Image
    multi_band: ee.Image
    region: ee.Geometry
    name_prefix: str


@dataclass(frozen=True, slots=True)
class LayerLegend:
    """A map layer paired with the legend shown when it is selected."""

    layer_id: str
    label: str
    data: LegendData


def _aoi_key(aoi_value) -> str:
    """Return a stable key for the current AOI selection."""
    if aoi_value is None:
        return ""

    return f"{aoi_value.method}:{aoi_value.name}"


def _upsert_legends(current: tuple, *new: LayerLegend) -> tuple:
    """Replace same-id legends in place and append the rest."""
    by_id = {legend.layer_id: legend for legend in current}
    by_id.update({legend.layer_id: legend for legend in new})
    return tuple(by_id.values())


def _ndvi_composite() -> ee.Image:
    """Sentinel-2 NDVI over a fixed demo area, independent of the AOI."""
    polygons = ee.FeatureCollection(
        [
            ee.Feature(ee.Geometry.Rectangle([-74.15, 4.77, -74.10, 4.72]), {"name": "Tile A"}),
            ee.Feature(ee.Geometry.Rectangle([-74.09, 4.77, -74.04, 4.72]), {"name": "Tile B"}),
        ]
    )
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(polygons)
        .filterDate("2024-01-01", "2024-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
        .median()
    )

    return s2.normalizedDifference(["B8", "B4"]).rename("NDVI")


def _build_outputs(aoi_value) -> ProcessingOutputs:
    """Derive the demo Earth Engine outputs from the selected AOI."""
    fc = aoi_value.feature_collection

    # clipToCollection masks to the collection's features, so a dense AOI never
    # dissolves into one 2M-edge geometry the way clip(fc.geometry()) would
    # (issue #996). ee.Image.clip only accepts a Geometry/Feature, so a
    # FeatureCollection must go through clipToCollection.
    pixel_area = ee.Image.pixelArea().rename("pixel_area_m2").clipToCollection(fc)

    elevation = ee.Image("USGS/SRTMGL1_003").select("elevation")
    elevation_class = (
        ee.Image(1)
        .where(elevation.gte(500), 2)
        .where(elevation.gte(1500), 3)
        .updateMask(elevation.mask())
        .rename("elevation_class")
        .clipToCollection(fc)
    )

    multi_band = pixel_area.addBands(elevation_class).addBands(ee.Image.constant(1).rename("flag"))

    # Export region as the union of per-feature bounding boxes -- same trick as
    # clip, so exporting a dense AOI doesn't dissolve its geometry (issue #996).
    region = fc.map(lambda f: ee.Feature(f.geometry().bounds())).geometry().bounds()

    return ProcessingOutputs(
        pixel_area=pixel_area,
        elevation_class=elevation_class,
        multi_band=multi_band,
        region=region,
        name_prefix=aoi_value.name.replace(" ", "_"),
    )


def _gradient_legend(title: str, vis: dict) -> LegendData:
    """Build a continuous legend straight from a layer's vis_params."""
    return LegendData(
        gradients=[
            GradientEntry(
                colors=list(vis["palette"]),
                labels=[f"{vis['min']:g}", f"{vis['max']:g}"],
                title=title,
            )
        ]
    )


def _area_detail(area_km2: float, total_km2: float) -> str:
    """Format one legend detail cell as area plus share of the total."""
    share = (area_km2 / total_km2 * 100) if total_km2 else 0.0
    return f"{area_km2:,.0f} km² · {share:.0f}%"


async def _elevation_class_legend(gee_interface, outputs: ProcessingOutputs) -> LegendData:
    """Reduce the classified image to per-class areas and put them in the legend.

    `DiscreteEntry.detail` is what makes this possible: the numbers ride along
    with the color chips instead of needing a separate results table.
    """
    grouped = (
        ee.Image.pixelArea()
        .addBands(outputs.elevation_class)
        .reduceRegion(
            reducer=ee.Reducer.sum().group(groupField=1, groupName="class"),
            geometry=outputs.region,
            scale=300,
            maxPixels=1e9,
            bestEffort=True,
        )
    )
    groups = (await gee_interface.get_info_async(grouped)).get("groups", [])
    area_by_class = {int(group["class"]): group["sum"] / 1e6 for group in groups}
    total = sum(area_by_class.values())

    items = [
        DiscreteEntry(label, color, detail=_area_detail(area_by_class.get(value, 0.0), total))
        for value, label, color in ELEVATION_CLASSES
    ]
    # An entry with no color renders without a chip, which reads as a totals row.
    items.append(DiscreteEntry("Total", "", detail=_area_detail(total, total)))

    return LegendData(items=items)


def _export_sources(aoi_value, outputs) -> list[ExportSource]:
    """Declare what the export dialog is allowed to offer.

    The dialog only lists datasets a page explicitly registers here.
    """
    sources: list[ExportSource] = []

    if aoi_value is not None and aoi_value.feature_collection is not None:
        sources.append(
            ExportSource(
                id="selected_aoi",
                label="Selected AOI boundary",
                kind="table",
                description="The AOI feature collection currently selected in the sidebar.",
                resolve=lambda fc=aoi_value.feature_collection, name=aoi_value.name: ResolvedExport(
                    ee_object=fc,
                    default_name=name,
                    drive_folder="pysepal_exports",
                    sepal_folder="exports",
                ),
            )
        )

    if outputs is None:
        return sources

    def image_source(source_id, label, image, description, bands=None, default_bands=None):
        return ExportSource(
            id=source_id,
            label=label,
            kind="image",
            description=description,
            resolve=lambda: ResolvedExport(
                ee_object=image,
                default_name=f"{outputs.name_prefix}_{source_id}",
                region=outputs.region,
                default_scale=300,
                bands=bands,
                default_bands=default_bands,
                drive_folder="pysepal_exports",
                sepal_folder="exports",
            ),
        )

    sources += [
        image_source(
            "pixel_area",
            "Pixel area (m²)",
            outputs.pixel_area,
            "Continuous output. Its map legend is the gradient built from vis_params.",
        ),
        image_source(
            "elevation_class",
            "Elevation classes",
            outputs.elevation_class,
            "Classified output. Its legend lists per-class areas in the detail column.",
        ),
        image_source(
            "multi_band",
            "Multi-band demo (3 bands)",
            outputs.multi_band,
            "Shows the ExportLauncher band picker: keep every band or narrow to a subset.",
            bands=("pixel_area_m2", "elevation_class", "flag"),
            # Pre-select the useful bands; `flag` stays deselectable from the dialog.
            default_bands=("pixel_area_m2", "elevation_class"),
        ),
    ]

    return sources


@solara.component
def ProcessPanel(aoi_data, outputs, layer_legends, sepal_map, gee_interface):
    """Run the demo processing, add its layers and publish their legends."""
    notifications = use_notifications()

    async def run_process():
        if aoi_data.value is None or aoi_data.value.feature_collection is None:
            raise ValueError("Select an AOI first before running processing.")

        built = _build_outputs(aoi_data.value)

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
            class_legend = await _elevation_class_legend(gee_interface, built)
            task.set_progress(0.9)

            task.step("Publishing legends and export sources...")
            layer_legends.set(
                _upsert_legends(
                    layer_legends.value,
                    LayerLegend(
                        PIXEL_AREA_LAYER_ID,
                        "Pixel area (m²)",
                        _gradient_legend("Pixel area (m²)", PIXEL_AREA_VIS),
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


@solara.component
def ExportPanel(aoi_data, outputs, gee_interface, drive_interface):
    """Export the selected AOI and any processed outputs.

    The interfaces are threaded in rather than looked up here. Both
    ``get_current_gee_interface`` and ``get_current_drive_interface`` raise once
    the SessionManager is live but the current render has no session, and this
    panel is rendered as a child of MapApp's right panel -- a separate render
    root from the ``@with_sepal_sessions`` page that establishes the session.
    Resolving them once at the top of :func:`MapAppDemo` keeps the lookup where
    the session is known to exist.
    """
    ExportLauncher(
        sources=_export_sources(aoi_data.value, outputs.value),
        dialog_title="Export datasets",
        default_target="gee",
        button_text=True,
        block=True,
        gee_interface=gee_interface,
        drive_interface=drive_interface,
    )


@solara.component
def MapAppDemo():
    """MapApp shell wiring AOI, processing, layers, legend and export together."""
    setup_theme_colors()

    gee_interface = get_current_gee_interface()
    drive_interface = get_current_drive_interface()
    theme_state = get_current_theme_state()

    aoi_data = solara.use_reactive(None)
    aoi_loading = solara.use_reactive(False)
    outputs = solara.use_reactive(None)
    layer_legends = solara.use_reactive(())
    selected_legend = solara.use_reactive("")

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
    app_model = solara.use_memo(AppModel, [])

    async def add_ndvi_layer():
        """Add the demo layer.

        Scheduled through ``use_task`` rather than ``gee_interface.create_task``: the
        latter runs on GEEInterface's own event loop, and two loops sharing the
        eeclient http/2 client crash it mid-request.
        """
        await sepal_map.add_ee_layer_async(
            _ndvi_composite(),
            vis_params=NDVI_VIS,
            name="Sentinel-2 NDVI",
            key=NDVI_LAYER_ID,
        )
        sepal_map.center = DEMO_CENTER
        sepal_map.zoom = 12
        layer_legends.set(
            _upsert_legends(
                layer_legends.value,
                LayerLegend(NDVI_LAYER_ID, "Sentinel-2 NDVI", _gradient_legend("NDVI", NDVI_VIS)),
            )
        )

    ndvi_task = solara.lab.use_task(
        add_ndvi_layer, dependencies=None, raise_error=False, prefer_threaded=False
    )
    ndvi_btn_props = use_task_button(ndvi_task, on_start=ndvi_task)

    def build_layer_buttons():
        """Build the sync ipyvuetify buttons once; they close over stable reactives."""
        btn_pmtiles = sw.Btn("add pmtiles layer", small=True, block=True)
        btn_remove = sw.Btn("remove all layers", small=True, block=True)

        def add_pmtiles_layer():
            """Add vector tiles, which the layer control drives without Earth Engine."""
            sepal_map.add_layer(
                PMTilesLayer(name="NZ buildings", url=PMTILES_URL, style=PMTILES_STYLE),
                key=PMTILES_LAYER_ID,
            )
            sepal_map.center = PMTILES_CENTER
            sepal_map.zoom = 14

        def remove_all_layers():
            sepal_map.remove_all()
            sepal_map.center = DEMO_CENTER
            sepal_map.zoom = 5
            layer_legends.set(())
            outputs.set(None)

        btn_pmtiles.on_event("click", lambda *args: add_pmtiles_layer())
        btn_remove.on_event("click", lambda *args: remove_all_layers())
        return btn_pmtiles, btn_remove

    btn_pmtiles, btn_remove = solara.use_memo(build_layer_buttons, [id(gee_interface)])

    aoi_key = _aoi_key(aoi_data.value)
    previous_aoi_key = solara.use_ref(aoi_key)

    def _drop_stale_outputs():
        """Processed layers belong to one AOI; retire them when it changes."""
        if previous_aoi_key.current == aoi_key:
            return

        for layer_id in AOI_LAYER_IDS:
            sepal_map.remove_layer(layer_id, none_ok=True)

        outputs.set(None)
        layer_legends.set(
            tuple(entry for entry in layer_legends.value if entry.layer_id not in AOI_LAYER_IDS)
        )
        previous_aoi_key.current = aoi_key

    solara.use_effect(_drop_stale_outputs, [aoi_key])

    legends = layer_legends.value
    current_legend = next(
        (entry for entry in legends if entry.layer_id == selected_legend.value), None
    )
    # Falling back to the first entry is not cosmetic: the legend only renders
    # while it has gradients or items, so an unmatched selection would take the
    # layer dropdown down with it and leave no way back.
    current_legend = current_legend or (legends[0] if legends else None)

    aoi_view = AoiView(
        value=aoi_data,
        loading=aoi_loading,
        methods="ALL",
        map_=sepal_map,
        gee=True,
        file_initial_folder=str(DUMMY_DATA_DIR),
    )

    right_panel_config = {
        "title": "Tools",
        "icon": "mdi-map-marker-check",
        "width": 400,
        "description": "Select an area, process it, then inspect and export the results.",
    }

    right_panel_content = [
        {
            "title": "Select AOI",
            "icon": "mdi-map-marker-check",
            "content": [aoi_view],
        },
        {
            "title": "Process",
            "icon": "mdi-cog-outline",
            "content": [
                ProcessPanel(
                    aoi_data=aoi_data,
                    outputs=outputs,
                    layer_legends=layer_legends,
                    sepal_map=sepal_map,
                    gee_interface=gee_interface,
                )
            ],
            "description": "Derives two layers from the AOI and publishes a legend for each.",
        },
        {
            "title": "Layers",
            "icon": "mdi-layers",
            "content": [
                TaskButtonComponent(label="add layer", **ndvi_btn_props, small=True, block=True),
                btn_pmtiles,
                btn_remove,
                AdminButton(app_model, logger_instance=logger),
            ],
            "description": (
                "Add a standalone demo layer or a PMTiles vector layer, or clear the map "
                "and its legends. Both show up in the layer control, top right."
            ),
            "divider": True,
        },
        {
            "title": "Export",
            "icon": "mdi-export-variant",
            "content": [
                ExportPanel(
                    aoi_data=aoi_data,
                    outputs=outputs,
                    gee_interface=gee_interface,
                    drive_interface=drive_interface,
                )
            ],
            "description": "Send the AOI or a processed output to Earth Engine, Drive or SEPAL.",
        },
    ]

    # Toasts top-right, task progress pill bottom-right.
    NotificationProvider()

    # Floats bottom-center over the map. The dropdown appears once two or more
    # layers publish a legend; a single layer renders its legend on its own.
    LegendComponent(
        legend_data=asdict(current_legend.data) if current_legend else {},
        selector_options=[{"value": entry.layer_id, "text": entry.label} for entry in legends],
        selected=current_legend.layer_id if current_legend else "",
        event_set_selected=selected_legend.set,
    )

    MapApp.element(
        app_title="PySepal Map App",
        app_icon="mdi-earth",
        main_map=[sepal_map],
        steps_data=[],
        right_panel_config=right_panel_config,
        right_panel_content=right_panel_content,
        right_panel_open=True,
        theme_state=theme_state,
        dialog_width=750,
    )


@solara.component
@with_sepal_sessions(module_name="solara_map_app")
def Page():
    """Authenticated Solara-server entrypoint for the map app demo."""
    MapAppDemo()
