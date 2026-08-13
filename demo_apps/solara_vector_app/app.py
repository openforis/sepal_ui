"""Vector tiles from a local file: convert once, then style the archive.

Two buttons over one PMTiles archive built by ``vectortileserver``: a single
symbol, and one deterministic color per attribute value. The conversion runs
once and is cached by the workspace, so the second button restyles the same
archive rather than rebuilding it.

Unlike rasters, the browser reads PMTiles with HTTP range requests straight out
of the archive, so what reaches it is the file itself rather than tiles rendered
per request. See ``docs/guides/local-tile-servers.md`` for which transport
carries it in each deployment.

Set ``PYSEPAL_DEMO_VECTOR_DIR`` to a directory holding ``landcover.geojson`` to
run against real data; without it the demo generates a small grid so it still
runs anywhere.

The UI lives in :func:`VectorAppDemo` so the same code serves both runtimes --
``Page`` is the Solara entrypoint and ``ui.ipynb`` is a thin Voila one.

To run:

```bash
pysepal$ ./run_solara.sh demo_apps/solara_vector_app/app.py --port 8901
```
"""

import os
from pathlib import Path
from typing import Optional

import solara
from vectortileserver import TileWorkspace, categorized_style, single_symbol_style

import pysepal.sepalwidgets as sw
from pysepal import mapping as sm
from pysepal.scripts.scratch import scratch_root
from pysepal.sepalwidgets.vue_app import MapApp
from pysepal.solara import (
    get_current_theme_state,
    setup_solara_server,
    setup_theme_colors,
)
from pysepal.solara.components.task_button import TaskButtonComponent, use_task_button
from pysepal.solara.notifications import NotificationProvider, use_notifications

setup_solara_server(extra_asset_locations=[])

#: Points the demo at a real vector file instead of the generated stand-in.
VECTOR_DIR_ENV_VAR = "PYSEPAL_DEMO_VECTOR_DIR"

#: Browser-facing URL prefixes; see :func:`browser_facing_prefix`.
VECTOR_PREFIX_ENV_VAR = "VECTORTILESERVER_CLIENT_PREFIX"
RASTER_PREFIX_ENV_VAR = "LOCALTILESERVER_CLIENT_PREFIX"

#: The attribute the categorized style colors by, and the values it expects.
LANDCOVER_FIELD = "landcover"
LANDCOVER_CLASSES = ["forest", "savanna", "cropland", "wetland", "urban", "water"]


def _synthetic_vector(path: Path) -> Path:
    """Write a small polygon grid, so the demo runs without a real product."""
    import geopandas as gpd
    from shapely.geometry import box

    if path.exists():
        return path

    step = 0.05
    cells, classes = [], []
    for row in range(8):
        for column in range(8):
            west = 20 + column * step
            north = -row * step
            cells.append(box(west, north - step, west + step, north))
            classes.append(LANDCOVER_CLASSES[(row + column) % len(LANDCOVER_CLASSES)])

    path.parent.mkdir(parents=True, exist_ok=True)
    frame = gpd.GeoDataFrame({LANDCOVER_FIELD: classes, "geometry": cells}, crs="EPSG:4326")
    frame.to_file(path, driver="GeoJSON")

    return path


def browser_facing_prefix() -> Optional[str]:
    """Resolve the URL prefix the browser should use to reach the tile server.

    ``vectortileserver`` never autodetects one, and a host that sets only
    ``LOCALTILESERVER_CLIENT_PREFIX`` -- SEPAL does -- would leave PMTiles on a
    loopback URL that a remote browser cannot reach. That variable is safe to
    borrow only when it is jupyter-server-proxy's generic ``/proxy/{port}``
    route, which forwards any port in the sandbox; localtileserver's own
    autodetected value is namespaced to itself and would not serve ours.
    """
    prefix = os.environ.get(VECTOR_PREFIX_ENV_VAR)
    if prefix is not None:
        return prefix

    borrowed = os.environ.get(RASTER_PREFIX_ENV_VAR)
    return borrowed if borrowed and "/proxy/{port}" in borrowed else None


def demo_vector() -> dict:
    """Return the source to tile, generating a stand-in when absent."""
    directory = os.environ.get(VECTOR_DIR_ENV_VAR)
    if directory:
        source = Path(directory) / "landcover.geojson"
        if source.is_file():
            return {"source": source, "synthetic": False}

    scratch = scratch_root() / "pysepal-vector-demo"
    return {"source": _synthetic_vector(scratch / "landcover.geojson"), "synthetic": True}


@solara.component
def VectorAppDemo():
    """Mount the notification bus, then the app that publishes to it.

    ``use_notifications()`` resolves to a NoopNotifier while no provider is
    mounted, and the tasks close over whatever it returned -- so the hook has to
    run in a child of the provider, not alongside it.
    """
    # Toasts top-right, task progress pill bottom-right.
    NotificationProvider()
    VectorPanel()


@solara.component
def VectorPanel():
    """Map plus a panel of buttons, one per styling of the same archive."""
    setup_theme_colors()
    # Theme is scope-keyed UI state, so this reads nothing from the session --
    # which is what lets the demo run undecorated, and run inside the gallery
    # where the map app's session manager is active process-wide.
    theme_state = get_current_theme_state()
    notifications = use_notifications()

    vector = solara.use_memo(demo_vector, [])
    prefix = browser_facing_prefix()
    # The workspace caches the conversion per source, so both buttons pay for
    # tippecanoe once between them. Bind 127.0.0.1 rather than the default
    # "localhost": a SEPAL sandbox has no IPv6 loopback, and uvicorn tries ::1
    # first, so the server never comes up there.
    workspace = solara.use_memo(
        lambda: TileWorkspace(host="127.0.0.1", client_prefix=prefix), [prefix]
    )

    def build_map():
        return sm.SepalMap(
            zoom=3, center=[0, 0], gee=False, fullscreen=True, theme_state=theme_state
        )

    sepal_map = solara.use_memo(build_map, [])

    async def show(style, layer_name: str, key: str) -> None:
        """Convert if needed, then put the styled archive on the map."""
        layer = await workspace.open_async(vector["source"], style=style)
        layer.name = layer_name
        sepal_map.add_layer(layer, key=key)
        (south, west), (north, east) = layer.bounds
        sepal_map.zoom_bounds((west, south, east, north))

    async def add_single_symbol():
        """One color for every feature: the archive drawn with no attribute lookup."""
        with notifications.track("Single symbol") as task:
            task.step("building tiles...")
            await show(single_symbol_style(color="#2d6a4f"), "Landcover (single)", "single")
        notifications.success("Single symbol added")

    async def add_categorized():
        """A deterministic palette color per attribute value, from the same archive."""
        with notifications.track("Categorized") as task:
            task.step("styling tiles...")
            await show(
                categorized_style(field=LANDCOVER_FIELD, values=LANDCOVER_CLASSES),
                "Landcover (categorized)",
                "categorized",
            )
        notifications.success(f"{len(LANDCOVER_CLASSES)} categories added")

    single_task = solara.lab.use_task(
        add_single_symbol, dependencies=None, raise_error=False, prefer_threaded=False
    )
    categorized_task = solara.lab.use_task(
        add_categorized, dependencies=None, raise_error=False, prefer_threaded=False
    )

    single_props = use_task_button(single_task, on_start=single_task)
    categorized_props = use_task_button(categorized_task, on_start=categorized_task)

    def build_clear_button():
        """A plain ipyvuetify button, handed to MapApp intact with its handler."""
        button = sw.Btn("clear vectors", small=True, block=True)

        def clear():
            for key in ("single", "categorized"):
                sepal_map.remove_layer(key, none_ok=True)

        button.on_event("click", lambda *args: clear())
        return button

    clear_button = solara.use_memo(build_clear_button, [id(sepal_map)])

    source = "a generated grid" if vector["synthetic"] else "real data"

    MapApp.element(
        app_title="Vector tiles",
        app_icon="mdi-vector-square",
        main_map=[sepal_map],
        steps_data=[],
        right_panel_config={
            "title": "Vectors",
            "icon": "mdi-vector-polygon",
            "width": 380,
            "description": "Both buttons draw one PMTiles archive, styled two ways.",
        },
        right_panel_content=[
            {
                "title": "Local vectors",
                "icon": "mdi-vector-polygon",
                "content": [
                    TaskButtonComponent(
                        label="single symbol", **single_props, small=True, block=True
                    ),
                    TaskButtonComponent(
                        label="categorized", **categorized_props, small=True, block=True
                    ),
                    clear_button,
                ],
                "description": (
                    f"Tiling {source} with tippecanoe. The conversion is cached per "
                    f"source, so only the first button pays for it. Set "
                    f"{VECTOR_DIR_ENV_VAR} to use a real landcover.geojson."
                ),
            }
        ],
        right_panel_open=True,
        theme_state=theme_state,
        dialog_width=750,
    )


@solara.component
def Page():
    """Solara entrypoint -- no SEPAL session, the tiling path is entirely local."""
    VectorAppDemo()
