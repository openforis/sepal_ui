import uuid
from pathlib import Path

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
def root_dir():
    """
    Path to the root dir of the librairy
    """

    return Path(__file__).parents[1].absolute()


@pytest.fixture(scope="session")
def tmp_dir():
    """
    Creates a temporary local directory to store data
    """

    tmp_dir = Path.home() / "tmp" / "sepal_ui_tests"
    tmp_dir.mkdir(exist_ok=True, parents=True)

    return tmp_dir


@pytest.fixture(scope="session")
def gee_dir():
    """
    Create a test dir based on earthengine initialization
    populate it with fake super small assets:

    sepal-ui-<hash>/
    ├── folder1/
    │   └── point-featureCollection
    ├── point-featureCollection
    └── 4pixel-Image

    remove everything on teardown
    """
    if not ee.data._credentials:
        pytest.skip("Eathengine is not connected")

    # create a test folder with a hash name
    _hash = uuid.uuid4().hex
    root = ee.data.getAssetRoots()[0]["id"]
    gee_dir = Path(root) / f"sepal-ui-{_hash}"
    ee.data.createAsset({"type": "FOLDER"}, str(gee_dir))

    # create a subfolder
    subfolder = gee_dir / "subfolder"
    ee.data.createAsset({"type": "FOLDER"}, str(subfolder))

    # create test material

    center = sg.Point(0, 0)
    gdf = gpd.GeoDataFrame({"data": [0, 1], "geometry": [center, center]}, crs=4326)
    ee_gdf = ee.FeatureCollection(gdf.__geo_interface__)

    image = ee.Image.random().multiply(4).byte()
    ee_buffer = ee_gdf.first().geometry().buffer(200)
    image = image.clipToBoundsAndScale(ee_buffer, scale=100)

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


@pytest.fixture(scope="session")
def asset_france(gee_dir):
    """return the france asset available in our test account"""

    return f"{gee_dir}/france"


@pytest.fixture(scope="session")
def asset_italy(gee_dir):
    """return the italy asset available in our test account"""

    return f"{gee_dir}/italy"


@pytest.fixture(scope="session")
def asset_table_aoi(gee_dir):
    """return the aoi for the reclassify tests available in our test account"""

    return f"{gee_dir}/reclassify_table_aoi"


@pytest.fixture(scope="session")
def asset_image_aoi(gee_dir):
    """return the aoi for the reclassify tests available in our test account"""

    return f"{gee_dir}/reclassify_image_aoi"


@pytest.fixture(scope="session")
def no_name():
    """return a no-name tuple"""

    return ("no_name", "#000000")


@pytest.fixture
def alert():
    """return a dummy alert that can be used everywhere to display informations"""

    return sw.Alert()


@pytest.fixture(scope="session")
def readme(root_dir):
    """return the readme file path"""

    return root_dir / "README.rst"


@pytest.fixture(scope="session")
def asset_description():
    """return a test asset name"""

    return "test_travis"


@pytest.fixture(scope="session")
def asset_id(asset_description):
    """return a test asset id"""

    return f"users/bornToBeAlive/sepal_ui_test/{asset_description}"


@pytest.fixture(scope="session")
def asset_image_viz():
    """return a test asset id"""

    return "users/bornToBeAlive/sepal_ui_test/imageViZExample"
