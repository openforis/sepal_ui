"""AoiView must restore its picker state from a pre-populated ``value`` at mount.

Apps that persist AOI selections (project save/load) rebuild an ``AoiResult``
and pass it as ``value`` when remounting ``AoiView``. Without restore support
the picker renders blank (method select empty) even though ``value`` is set.

Covers every selection method: the picker must seed its method select (plus
the method-specific inputs it can) and auto-confirm the restored AOI — the
success feedback is the observable proof the auto-select ran without
reprocessing.
"""

import asyncio
import time

import geopandas as gpd
import pytest
import solara
from shapely.geometry import box as shapely_box

import pysepal.solara.components.aoi.admin as admin_mod
import pysepal.solara.components.aoi.aoi_view as aoi_view_mod
from pysepal.message import ms
from pysepal.solara.components.aoi import AoiResult
from pysepal.solara.components.aoi.aoi_view import AoiView


def _fake_fetch(level, parent_code):
    mapping = {
        (0, ""): [
            {"text": "Paraguay", "value": "206"},
            {"text": "Algeria", "value": "101"},
        ],
        (1, "206"): [{"text": "Amambay", "value": "2184"}],
        (1, "101"): [{"text": "Adrar", "value": "1001"}],
        (2, "1001"): [{"text": "Adrar", "value": "100001"}],
    }
    return mapping.get((level, str(parent_code)), [])


_CHAINS = {
    "197": {0: "197"},
    "206": {0: "206"},
    "2184": {0: "206", 1: "2184"},
    "100001": {0: "101", 1: "1001", 2: "100001"},
}


def _fake_chain(method, code):
    return dict(_CHAINS.get(str(code), {}))


def _gdf():
    return gpd.GeoDataFrame(
        {"name": ["aoi"]}, geometry=[shapely_box(12.40, 43.89, 12.52, 43.99)], crs="EPSG:4326"
    )


def _widgets(root):
    """Depth-first walk over an ipywidgets tree."""
    seen = set()
    stack = [root]
    while stack:
        widget = stack.pop()
        if id(widget) in seen:
            continue
        seen.add(id(widget))
        yield widget
        stack.extend(getattr(widget, "children", ()) or ())


def _has_v_model(root, expected):
    return any(getattr(w, "v_model", None) == expected for w in _widgets(root))


def _has_text(root, expected):
    for w in _widgets(root):
        for child in getattr(w, "children", ()) or ():
            if isinstance(child, str) and expected in child:
                return True
    return False


async def _settle(box, *predicates, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline and not all(p(box) for p in predicates):
        await asyncio.sleep(0.05)


def _patch_admin(monkeypatch):
    monkeypatch.setattr(admin_mod, "fetch_admin_items", _fake_fetch)
    monkeypatch.setattr(admin_mod, "admin_parent_chain", _fake_chain, raising=False)


@pytest.mark.parametrize(
    "result",
    [
        AoiResult(method="ADMIN0", name="Paraguay", admin="206", gee=False),
        AoiResult(method="ADMIN1", name="Amambay", admin="2184", gee=False),
        AoiResult(method="ADMIN2", name="Adrar", admin="100001", gee=False),
        AoiResult(method="SHAPE", name="my_shape", gdf=_gdf(), gee=False),
        AoiResult(method="POINTS", name="my_points", gdf=_gdf(), gee=False),
        AoiResult(method="DRAW", name="my_drawing", gdf=_gdf(), gee=False),
    ],
    ids=lambda r: r.method,
)
def test_aoi_view_restores_every_method_from_value(monkeypatch, result):
    _patch_admin(monkeypatch)

    value = solara.reactive(result)

    async def _scenario():
        box, rc = solara.render(AoiView(value=value, gee=False), handle_error=False)
        try:
            await _settle(
                box,
                lambda b: _has_v_model(b, result.method),
                lambda b: _has_text(b, ms.aoi_sel.complete),
            )
            assert _has_v_model(
                box, result.method
            ), f"method select was not seeded with {result.method}"
            # The auto-select must land the panel in the confirmed state.
            assert _has_text(
                box, ms.aoi_sel.complete
            ), f"restored {result.method} AOI was not auto-confirmed"
            # The restore must keep the loaded AOI, not clear or rebuild it.
            assert value.value is result
        finally:
            rc.close()

    asyncio.run(_scenario())


class _FakeDrawControl:
    def __init__(self):
        self.data = []

    def clear(self):
        pass

    def to_json(self):
        return {"features": self.data}


class _FakeMap:
    """Minimal SepalMap stand-in: draw control + layer/control bookkeeping."""

    def __init__(self):
        self.dc = _FakeDrawControl()
        self.controls = []
        self.layers = []

    def add_control(self, control):
        self.controls.append(control)

    def remove_control(self, control):
        self.controls.remove(control)

    def add_layer(self, layer, key=None):
        self.layers.append(layer)

    def remove_layer(self, layer):
        self.layers.remove(layer)

    def zoom_bounds(self, bounds):
        pass


def test_aoi_view_restores_draw_name_and_editable_geometry(monkeypatch):
    _patch_admin(monkeypatch)

    map_ = _FakeMap()
    result = AoiResult(method="DRAW", name="my_drawing", gdf=_gdf(), gee=False)
    value = solara.reactive(result)

    async def _scenario():
        box, rc = solara.render(AoiView(value=value, gee=False, map_=map_), handle_error=False)
        try:
            await _settle(
                box,
                lambda b: _has_v_model(b, "my_drawing"),
                lambda b: _has_text(b, ms.aoi_sel.complete),
            )
            # The DRAW name field must be seeded with the restored AOI name.
            assert _has_v_model(box, "my_drawing"), "draw name field was not restored"
            assert _has_text(box, ms.aoi_sel.complete), "restored DRAW AOI was not auto-confirmed"
            # The DrawControl must be re-populated so the restored AOI is editable,
            # and the geometry re-rendered on the map by the auto-select.
            assert map_.dc.data, "DrawControl was not re-seeded from the restored gdf"
            assert map_.layers, "restored AOI layer was not drawn on the map"
        finally:
            rc.close()

    asyncio.run(_scenario())


def test_aoi_view_restores_admin_cascade_code(monkeypatch):
    _patch_admin(monkeypatch)

    result = AoiResult(method="ADMIN1", name="Amambay", admin="2184", gee=False)
    value = solara.reactive(result)

    async def _scenario():
        box, rc = solara.render(AoiView(value=value, gee=False), handle_error=False)
        try:
            # Both cascade levels must end up selected (parent + final code).
            await _settle(
                box,
                lambda b: _has_v_model(b, "206"),
                lambda b: _has_v_model(b, "2184"),
            )
            assert _has_v_model(box, "206"), "cascade parent (level 0) was not restored"
            assert _has_v_model(box, "2184"), "cascade final code (level 1) was not restored"
        finally:
            rc.close()

    asyncio.run(_scenario())


class _FakeGeeInterface:
    async def get_folder_async(self):
        return "users/me"

    async def get_assets_async(self, folder):
        return []

    async def get_asset_async(self, asset_id):
        raise ValueError("no GEE access in tests")


def test_aoi_view_restores_asset_selection(monkeypatch):
    _patch_admin(monkeypatch)
    monkeypatch.setattr(aoi_view_mod.su, "init_ee", lambda: None)
    monkeypatch.setattr(aoi_view_mod, "get_current_gee_interface", lambda: _FakeGeeInterface())

    asset = {"asset_id": "users/me/aoi", "type": "TABLE", "column": "ALL", "value": None}
    result = AoiResult(method="ASSET", name="aoi", gee=True, asset=asset)
    value = solara.reactive(result)

    async def _scenario():
        box, rc = solara.render(AoiView(value=value, gee=True), handle_error=False)
        try:
            await _settle(
                box,
                lambda b: _has_v_model(b, "ASSET"),
                lambda b: _has_v_model(b, "users/me/aoi"),
                lambda b: _has_text(b, ms.aoi_sel.complete),
            )
            assert _has_v_model(box, "ASSET"), "method select was not seeded with ASSET"
            # The asset combobox must be seeded from AoiResult.asset.
            assert _has_v_model(box, "users/me/aoi"), "asset id was not restored"
            assert _has_text(box, ms.aoi_sel.complete), "restored ASSET AOI was not auto-confirmed"
            assert value.value is result
        finally:
            rc.close()

    asyncio.run(_scenario())
