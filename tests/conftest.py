import uuid
from itertools import product
from pathlib import Path
from typing import Optional

import ee
import geopandas as gpd
import pytest
from shapely import geometry as sg

import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su

# try to init earthengine. if it does not work the non existing credentials will
# be used to skpip
try:
    su.init_ee()
except Exception:
    pass


@pytest.fixture(scope="session")
def root_dir() -> Path:
    """
    Path to the root dir of the librairy.
    """
    return Path(__file__).parents[1].absolute()


@pytest.fixture(scope="session")
def tmp_dir() -> Path:
    """
    Creates a temporary local directory to store data.
    """
    tmp_dir = Path.home() / "tmp" / "sepal_ui_tests"
    tmp_dir.mkdir(exist_ok=True, parents=True)

    return tmp_dir


@pytest.fixture(scope="session")
def _hash() -> str:
    """
    Create a hash for each test instance.
    """
    return uuid.uuid4().hex


@pytest.fixture(scope="session")
def gee_dir(_hash: str) -> Optional[Path]:
    """
    Create a test dir based on earthengine initialization
    populate it with fake super small assets:

    sepal-ui-<hash>/
    ├── subfolder/
    │   └── subfolder_feature_collection
    ├── feature_collection
    └── image

    remove everything on teardown
    """
    if not ee.data._credentials:
        pytest.skip("Eathengine is not connected")

    # create a test folder with a hash name
    root = ee.data.getAssetRoots()[0]["id"]
    gee_dir = Path(root) / f"sepal-ui-{_hash}"
    ee.data.createAsset({"type": "FOLDER"}, str(gee_dir))

    # create a subfolder
    subfolder = gee_dir / "subfolder"
    ee.data.createAsset({"type": "FOLDER"}, str(subfolder))

    # create test material
    centers = [sg.Point(i, j) for i, j in product([-50, 50], repeat=2)]
    data = list(range(len(centers)))
    gdf = gpd.GeoDataFrame({"data": data, "geometry": centers}, crs=3857).to_crs(4326)
    ee_gdf = ee.FeatureCollection(gdf.__geo_interface__)

    image = ee.Image.random().multiply(4).byte()

    lon = ee.Image.pixelLonLat().select("longitude")
    lat = ee.Image.pixelLonLat().select("latitude")
    image = (
        ee.Image(1)
        .where(lon.gt(0).And(lat.gt(0)), 2)
        .where(lon.lte(0).And(lat.lte(0)), 3)
        .where(lon.gt(0).And(lat.lte(0)), 4)
    )
    ee_buffer = ee.Geometry.Point(0, 0).buffer(200).bounds()
    image = image.clipToBoundsAndScale(ee_buffer, scale=30)

    # exports It should take less than 2 minutes unless there are concurent tasks
    fc = "feature_collection"
    ee.batch.Export.table.toAsset(
        collection=ee_gdf, description=f"{fc}_{_hash}", assetId=str(gee_dir / fc)
    ).start()

    subfolder_fc = "subfolder_feature_collection"
    ee.batch.Export.table.toAsset(
        collection=ee_gdf,
        description=f"{subfolder_fc}_{_hash}",
        assetId=str(subfolder / subfolder_fc),
    ).start()

    rand_image = "image"
    ee.batch.Export.image.toAsset(
        image=image,
        description=f"{rand_image}_{_hash}",
        assetId=str(gee_dir / rand_image),
        region=ee_buffer,
    ).start()

    # wait for completion of the exportation tasks before leaving this method
    # image should be the longest
    gee.wait_for_completion(f"{fc}_{_hash}")
    gee.wait_for_completion(f"{subfolder_fc}_{_hash}")
    gee.wait_for_completion(f"{rand_image}_{_hash}")

    yield gee_dir

    # flush the directory and it's content
    ee.data.deleteAsset(str(subfolder / subfolder_fc))
    ee.data.deleteAsset(str(subfolder))
    ee.data.deleteAsset(str(gee_dir / fc))
    ee.data.deleteAsset(str(gee_dir / rand_image))
    ee.data.deleteAsset(str(gee_dir))

    return


@pytest.fixture
def alert() -> sw.Alert:
    """return a dummy alert that can be used everywhere to display informations."""
    return sw.Alert()
