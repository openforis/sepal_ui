"""Test AoiModel custom model."""

import math
from pathlib import Path
from typing import List, Tuple

import ee
import pytest
from traitlets import Dict, Unicode

from sepal_ui import aoi


def test_init_no_ee(fake_vector: Path) -> None:
    """Init an AoiModel without GEE.

    Args:
        fake_vector: the path to a fake vector file
    """
    # default init
    aoi_model = aoi.AoiModel(gee=False)
    assert isinstance(aoi_model, aoi.AoiModel)
    assert aoi_model.gee is False

    # with a default vector
    aoi_model = aoi.AoiModel(vector=fake_vector, gee=False)
    assert aoi_model.name == "gadm41_VAT_0"

    # test with a non ee admin
    admin = "VAT"  # GADM Vatican city
    aoi_model = aoi.AoiModel(gee=False, admin=admin)

    assert aoi_model.name == "VAT"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_init_ee(gee_dir: Path) -> None:
    """Init an AoiMOdel with GEE.

    Args:
        gee_dir: the session directory where assets are saved
    """
    # default init
    aoi_model = aoi.AoiModel(folder=gee_dir)
    assert isinstance(aoi_model, aoi.AoiModel)
    assert aoi_model.gee is True

    # with default assetId
    asset_id = str(gee_dir / "feature_collection")
    aoi_model = aoi.AoiModel(asset=asset_id, folder=gee_dir)

    assert aoi_model.asset_name == asset_id
    assert aoi_model.default_asset == asset_id
    assert all(aoi_model.gdf) is not None
    assert aoi_model.feature_collection is not None
    assert aoi_model.name == "feature_collection"

    # check that wrongly defined asset_name raise errors
    with pytest.raises(Exception):
        aoi_model = aoi.AoiModel(folder=gee_dir)
        aoi_model._from_asset({"pathname": None})

    with pytest.raises(Exception):
        aoi_model = aoi.AoiModel(folder=gee_dir)
        asset = {"pathname": asset_id, "column": "data", "value": None}
        aoi_model._from_asset(asset)

    # it should be the same with a different name
    aoi_model = aoi.AoiModel(folder=gee_dir)
    asset = {"pathname": asset_id, "column": "data", "value": 0}
    aoi_model._from_asset(asset)
    assert aoi_model.name == "feature_collection_data_0"

    # with a default admin
    admin = "110"  # GAUL Vatican city
    aoi_model = aoi.AoiModel(admin=admin, folder=gee_dir)
    assert aoi_model.name == "VAT"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_columns(test_model: aoi.AoiModel, test_columns: List[str]) -> None:
    """Get the columns from a selected geometry.

    Args:
        test_model: an object set on Vatican city
        test_columns: the columns name of a AoiMOdel object
    """
    # test that before any data is set the method raise an error
    with pytest.raises(Exception):
        aoi_model = aoi.AoiModel()
        aoi_model.get_columns()

    # test data
    res = test_model.get_columns()
    assert res == test_columns

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_fields(test_model: aoi.AoiModel) -> None:
    """Get fields from a selected geometry.

    Args:
        test_model: a model set on the vatican city
    """
    # test that before any data is set the method raise an error
    with pytest.raises(Exception):
        aoi_model = aoi.AoiModel()
        aoi_model.get_fields("toto")

    # init
    column = "ADM0_CODE"
    res = test_model.get_fields(column)
    assert res == [110]

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_selected(test_model: aoi.AoiModel) -> None:
    """Get fields from a selected geometry.

    Args:
        test_model: a model set on the vatican city
    """
    # test that before any data is set the method raise an error
    with pytest.raises(Exception):
        aoi_model = aoi.AoiModel()
        aoi_model.get_fields("toto", "toto")

    # select the vatican feature in GAUL 2015
    ee_vat = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(
        ee.Filter.eq("ADM0_CODE", "110")
    )

    # select the geometry associated with Vatican city (all of it)
    column, field = ("ADM0_CODE", "110")
    feature = test_model.get_selected(column, field)

    # assert they are the same
    dif = feature.geometry().difference(ee_vat.geometry()).coordinates().length()
    assert dif.getInfo() == 0

    return


def test_clear_attributes(
    aoi_model_outputs: List[str], aoi_model_traits: List[str]
) -> None:
    """Remove all attributes from an AoiMOdel.

    Args:
        aoi_model_outputs: the name of the object outputs
        aoi_model_traits: the name of the object traits
    """
    aoi_model = aoi.AoiModel(gee=False)

    # insert dum parameter everywhere
    def set_trait(trait_id: str) -> None:
        trait_type = aoi_model.traits()[trait_id]
        if isinstance(trait_type, Unicode):
            dum = "dum"
        elif isinstance(trait_type, Dict):
            dum = {"dum": "dum"}
        return setattr(aoi_model, trait_id, dum)

    def set_out(out_id: str) -> None:
        return setattr(aoi_model, out_id, "dum")

    [set_trait(trait) for trait in aoi_model_traits]
    [set_out(out) for out in aoi_model_outputs]

    # clear all the parameters
    aoi_model.clear_attributes()

    # create a function for readability
    def is_none(member: str) -> None:
        return getattr(aoi_model, member) is None

    assert all([is_none(trait) for trait in aoi_model_traits])
    assert all([is_none(out) for out in aoi_model_outputs])

    # check that default are saved
    aoi_model = aoi.AoiModel(admin="VAT", gee=False)  # GADM for Vatican

    # insert dummy parameter
    [set_trait(trait) for trait in aoi_model_traits]
    [set_out(out) for out in aoi_model_outputs]

    # clear
    aoi_model.clear_attributes()

    # assert that it's still Vatican
    assert aoi_model.name == "VAT"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_total_bounds(test_model: aoi.AoiModel, test_bounds: Tuple[float]) -> None:
    """Check that total bouds of the vatican are as expected.

    Args:
        test_model: a AoiMOdel object set on Vatican city
        test_bounds: the bounds of the expected geometry
    """
    bounds = test_model.total_bounds()
    assert all([math.isclose(b, t) for b, t in zip(bounds, test_bounds)])

    with pytest.raises(ValueError):
        test_model.clear_output()
        test_model.total_bounds()

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_clear_output(test_model: aoi.AoiModel, aoi_model_outputs: List[str]) -> None:
    """Clear all output from a AoiModel.

    Args:
        test_model: a aoi_model set on vatican city
        aoi_model_outputs: the name of the output members of the aoi_model object
    """
    # create functions for readability
    def is_not_none(member):
        return getattr(test_model, member) is not None

    def is_none(member):
        return getattr(test_model, member) is None

    # test that the data are not all empty
    assert any([is_not_none(out) for out in aoi_model_outputs])

    # clear the aoi outputs
    test_model.clear_output()
    assert all([is_none(out) for out in aoi_model_outputs])

    return


def test_set_object() -> None:
    """Set object without parameters."""
    aoi_model = aoi.AoiModel(gee=False)

    # test that no method returns an error
    with pytest.raises(Exception):
        aoi_model.set_object()

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_from_admin(gee_dir: Path) -> None:
    """Get an AoiMOdel from an admin value.

    Args:
        gee_dir: the path to the session gee_dir folder (including hash)
    """
    aoi_model = aoi.AoiModel(folder=gee_dir)

    # with fake number
    with pytest.raises(Exception):
        aoi_model._from_admin(0)

    # test france
    aoi_model._from_admin("110")
    assert aoi_model.name == "VAT"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_from_point(fake_points: Path, gee_dir: Path) -> None:
    """Get an AoiModel from point file.

    Args:
        gee_dir: the path to the session gee_dir folder (including hash)
        fake_points: the path to the point file
    """
    aoi_model = aoi.AoiModel(folder=gee_dir, gee=False)

    # uncomplete json
    points = {
        "pathname": None,
        "id_column": "id",
        "lat_column": "lat",
        "lng_column": "lon",
    }
    with pytest.raises(Exception):
        aoi_model._from_points(points)

    # complete
    points = {
        "pathname": fake_points,
        "id_column": "id",
        "lat_column": "lat",
        "lng_column": "lon",
    }
    aoi_model._from_points(points)
    assert aoi_model.name.startswith("tmp")

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_from_vector(gee_dir: Path, fake_vector: dict) -> None:
    """Get an AoiModel from a vector.

    Args:
        gee_dir: the path to the session gee_dir folder (including hash)
        fake_vector: the path to a vector file
    """
    aoi_model = aoi.AoiModel(folder=gee_dir, gee=False)

    # with no pathname
    with pytest.raises(Exception):
        aoi_model._from_vector(fake_vector)

    # only pathname and all
    vector = {"pathname": fake_vector, "column": "ALL", "value": None}
    aoi_model._from_vector(vector)
    assert aoi_model.name == "gadm41_VAT_0"

    # all params
    vector = {"pathname": fake_vector, "column": "GID_0", "value": "VAT"}
    aoi_model._from_vector(vector)
    assert aoi_model.name == "gadm41_VAT_0_GID_0_VAT"

    # missing value
    vector = {"pathname": fake_vector, "column": "GID_0", "value": None}
    with pytest.raises(Exception):
        aoi_model._from_vector(vector)

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_from_geo_json(gee_dir, square: dict) -> None:
    """Get an AoiModel from a geojson (equivalent to draw).

    Args:
        gee_dir: the path to the session gee_dir folder (including hash)
        square; the geo_interface representation of a quare around vatican
    """
    aoi_model = aoi.AoiModel(folder=gee_dir, gee=False)

    # no points
    with pytest.raises(Exception):
        aoi_model._from_geo_json({})

    # fully qualified square
    aoi_model.name = "square"
    aoi_model._from_geo_json(square)
    assert aoi_model.name == "square"

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_from_asset(gee_dir: Path) -> Path:
    """Get an AoiModel from gee assets.

    Args:
        gee_dir: the path to the session gee_dir folder (including hash)
    """
    # init parameters
    asset_id = str(gee_dir / "feature_collection")
    aoi_model = aoi.AoiModel(folder=gee_dir)

    # no asset name
    with pytest.raises(Exception):
        aoi_model._from_asset(asset_id)

    # only pathname and all
    asset = {"pathname": asset_id, "column": "ALL", "value": None}
    aoi_model._from_asset(asset)
    assert aoi_model.name == "feature_collection"

    # all params
    asset = {"pathname": asset_id, "column": "data", "value": 0}
    aoi_model._from_asset(asset)
    assert aoi_model.name == "feature_collection_data_0"

    # missing value
    asset = {"pathname": asset_id, "column": "data", "value": None}

    with pytest.raises(Exception):
        aoi_model._from_asset(asset)

    return


@pytest.fixture
def square() -> dict:
    """A geojson square around the vatican city.

    Returns:
        the geo_interface desciption of the square
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [12.445173, 41.899176],
                            [12.445173, 41.908813],
                            [12.4592, 41.908813],
                            [12.4592, 41.899176],
                            [12.445173, 41.899176],
                        ]
                    ],
                },
            }
        ],
    }


@pytest.fixture
def test_model(gee_dir: Path) -> aoi.AoiModel:
    """Create a test AoiModel based on GEE using Vatican.

    Args:
        gee_dir: the path to the session gee_dir folder (including hash)

    Returns:
        the model object
    """
    admin = "110"  # vatican city (smalest adm0 feature)
    return aoi.AoiModel(admin=admin, folder=gee_dir)


@pytest.fixture
def aoi_model_traits() -> List[str]:
    """Return the list of an aoi model traits.

    Returns:
        the model traits
    """
    return [
        "method",
        "point_json",
        "vector_json",
        "geo_json",
        "admin",
        "asset_json",
        "asset_name",
        "name",
    ]


@pytest.fixture
def aoi_model_outputs() -> List[str]:
    """Return the list of an aoi model outputs.

    Returns:
        the outputs of the model
    """
    return [
        "gdf",
        "feature_collection",
        "ipygeojson",
        "selected_feature",
        "dst_asset_id",
    ]


@pytest.fixture
def test_columns() -> List[str]:
    """Returns the column of the test vatican aoi.

    Returns:
        the column names
    """
    return [
        "ADM0_CODE",
        "ADM0_NAME",
        "DISP_AREA",
        "EXP0_YEAR",
        "STATUS",
        "STR0_YEAR",
        "Shape_Leng",
    ]


@pytest.fixture
def test_bounds() -> Tuple[float]:
    """Returns the bounds of the vatican asset.

    Returns:
        the bounds of vatican
    """
    return (
        12.445770205631668,
        41.90021953934405,
        12.457671530175347,
        41.90667181034752,
    )
