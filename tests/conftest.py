import geopandas as gpd
import pytest
from pathlib import Path
from zipfile import ZipFile
from urllib.request import urlretrieve
import os

import sepal_ui.sepalwidgets as sw
from sepal_ui.aoi import AoiModel


@pytest.fixture(scope="session")
def gee_ready():
    """return if exporting is possible with the current GEE authentification method"""

    return "EE_DECRYPT_KEY" not in os.environ


@pytest.fixture(scope="session")
def root_dir():
    """path to the root dir of the librairy"""

    return Path(__file__).parents[1].absolute()


@pytest.fixture(scope="session")
def tmp_dir():
    """Creates a temporary local directory"""

    tmp_dir = Path.home() / "tmp" / "sepal_ui_tests"
    tmp_dir.mkdir(exist_ok=True, parents=True)

    return tmp_dir


@pytest.fixture(scope="session")
def gee_dir():
    """the test dir allowed with the service account credentials"""

    return "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"


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
