"""Tests for process_asset."""

import asyncio

import pytest

from pysepal.solara.components.aoi import asset as asset_mod


def _run(coro):
    return asyncio.run(coro)


class _FakeFeatureCollection:
    def __init__(self, asset_id):
        self.asset_id = asset_id
        self.filters = []

    def filter(self, flt):
        self.filters.append(flt)
        return self


class _FakeImage:
    def __init__(self, asset_id):
        self.asset_id = asset_id


class _FakeFilter:
    def __init__(self):
        self.calls = []

    def eq(self, column, value):
        self.calls.append((column, value))
        return ("eq", column, value)


@pytest.fixture
def fake_ee(monkeypatch):
    created = []

    def fc(asset_id):
        obj = _FakeFeatureCollection(asset_id)
        created.append(("fc", obj))
        return obj

    def img(asset_id):
        obj = _FakeImage(asset_id)
        created.append(("img", obj))
        return obj

    class _FakeEe:
        FeatureCollection = staticmethod(fc)
        Image = staticmethod(img)
        ImageCollection = staticmethod(img)
        Filter = _FakeFilter()

    monkeypatch.setattr(asset_mod, "ee", _FakeEe)
    monkeypatch.setattr(asset_mod.su, "init_ee", lambda: None)
    return created


def test_process_asset_rejects_empty_asset_id():
    with pytest.raises(ValueError, match="No GEE asset"):
        _run(asset_mod.process_asset(""))


def test_process_asset_rejects_column_filter_on_non_table(fake_ee):
    with pytest.raises(ValueError, match="only available for TABLE"):
        _run(asset_mod.process_asset("users/me/img", asset_type="IMAGE", column="region"))


def test_process_asset_rejects_column_without_value(fake_ee):
    with pytest.raises(ValueError, match="select a value"):
        _run(
            asset_mod.process_asset("users/me/tab", asset_type="TABLE", column="region", value=None)
        )


def test_process_asset_rejects_unsupported_asset_type(fake_ee):
    with pytest.raises(ValueError, match="Unsupported asset type"):
        _run(asset_mod.process_asset("users/me/x", asset_type="FOLDER"))


def test_process_asset_table_unfiltered(fake_ee):
    result = _run(asset_mod.process_asset("users/me/my_table", asset_type="TABLE"))

    assert result.method == "ASSET"
    assert result.gee is True
    assert result.gdf is None
    assert result.name == "my_table"
    assert isinstance(result.feature_collection, _FakeFeatureCollection)


def test_process_asset_table_filtered_names_include_value(fake_ee):
    result = _run(
        asset_mod.process_asset(
            "users/me/my_table",
            asset_type="TABLE",
            column="region",
            value="north",
        )
    )

    assert result.name == "my_table_north"
    assert result.feature_collection.filters == [("eq", "region", "north")]


@pytest.mark.parametrize("asset_type", ["IMAGE", "IMAGE_COLLECTION"])
def test_process_asset_raster_types(fake_ee, asset_type):
    result = _run(asset_mod.process_asset("users/me/raster_asset", asset_type=asset_type))

    assert isinstance(result.feature_collection, _FakeImage)


def test_process_asset_attaches_selection_inputs(fake_ee):
    """The result must round-trip the picker inputs so apps can restore it."""
    result = _run(
        asset_mod.process_asset(
            "users/me/my_table",
            asset_type="TABLE",
            column="region",
            value="north",
        )
    )

    assert result.asset == {
        "asset_id": "users/me/my_table",
        "type": "TABLE",
        "column": "region",
        "value": "north",
    }


def test_aoi_result_asset_defaults_to_none():
    from pysepal.solara.components.aoi import AoiResult

    result = AoiResult(method="DRAW", name="drawn_item")
    assert result.asset is None
