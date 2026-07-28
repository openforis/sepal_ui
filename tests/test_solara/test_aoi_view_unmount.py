"""Unmounting AoiView must not erase the caller's AOI state.

``value`` may be a reactive owned by the host app (``solara.use_reactive``
passes a reactive straight through), so anything AoiView writes to it lands in
application state. Tearing the picker down — a collapsed panel, a conditional
render, a keyed remount — is a lifecycle event of the *widget*, not a user
decision to drop the AOI. Clearing ``value`` there silently destroys a
selection the app is still holding (and, for apps that persist it, saves an
empty AOI over a good one).

AoiView still owns the map layers, draw control and loading flag it created,
so unmount must keep releasing those.
"""

import asyncio

import geopandas as gpd
import solara
from shapely.geometry import box as shapely_box

from pysepal.solara.components.aoi import AoiResult
from pysepal.solara.components.aoi.aoi_view import AoiView

from .test_aoi_view_restore import _FakeMap


def _gdf():
    return gpd.GeoDataFrame(
        {"name": ["aoi"]},
        geometry=[shapely_box(12.40, 43.89, 12.52, 43.99)],
        crs="EPSG:4326",
    )


@solara.component
def _Host(value, show, map_, loading):
    """A host that mounts the picker behind a toggle, as a collapsible panel would."""
    with solara.Column():
        if show:
            AoiView(value=value, loading=loading, gee=False, map_=map_, methods="ALL")
        else:
            solara.Text("picker hidden")


def _run(scenario):
    asyncio.run(scenario())


def test_unmount_keeps_caller_owned_value():
    """The host's AOI reactive must survive the picker being unmounted."""
    map_ = _FakeMap()
    value = solara.reactive(AoiResult(method="DRAW", name="my_drawing", gdf=_gdf()))
    loading = solara.reactive(False)

    async def scenario():
        box, rc = solara.render(
            _Host(value=value, show=True, map_=map_, loading=loading),
            handle_error=False,
        )
        try:
            await asyncio.sleep(0.5)
            assert value.value is not None, "precondition: AOI is set while mounted"

            rc.render(_Host(value=value, show=False, map_=map_, loading=loading))
            await asyncio.sleep(0.5)

            assert value.value is not None, (
                "unmount cleared the caller's AOI reactive; the host app lost its "
                "selection just because the picker was torn down"
            )
            assert value.value.name == "my_drawing"
        finally:
            rc.close()

    _run(scenario)


def test_unmount_still_releases_owned_resources():
    """Unmount must keep tearing down what AoiView itself put on the map."""
    map_ = _FakeMap()
    value = solara.reactive(AoiResult(method="DRAW", name="my_drawing", gdf=_gdf()))
    loading = solara.reactive(True)

    async def scenario():
        box, rc = solara.render(
            _Host(value=value, show=True, map_=map_, loading=loading),
            handle_error=False,
        )
        try:
            await asyncio.sleep(0.8)

            rc.render(_Host(value=value, show=False, map_=map_, loading=loading))
            await asyncio.sleep(0.5)

            aoi_layers = [layer for layer in map_.layers if getattr(layer, "name", None) == "aoi"]
            assert not aoi_layers, "unmount left the AOI layer on the map"
            assert map_.dc not in map_.controls, "unmount left the DrawControl attached"
            assert loading.value is False, "unmount left the loading flag set"
        finally:
            rc.close()

    _run(scenario)
