import geopandas as gpd
import pytest
from pathlib import Path
from zipfile import ZipFile
from urllib.request import urlretrieve
import os

import sepal_ui.sepalwidgets as sw
from sepal_ui.aoi import AoiModel


@pytest.fixture
def gee_ready(scope="session"):
    """return if exporting is possible with the current GEE authentification method"""

    return "EE_DECRYPT_KEY" not in os.environ


@pytest.fixture
def root_dir(scope="session"):
    """path to the root dir of the librairy"""

    return Path(__file__).parents[1].absolute()


@pytest.fixture
def tmp_dir(scope="session"):
    """Creates a temporary local directory"""

    tmp_dir = Path.home() / "tmp" / "sepal_ui_tests"
    tmp_dir.mkdir(exist_ok=True, parents=True)

    return tmp_dir


@pytest.fixture
def gee_dir(scope="session"):
    """the test dir allowed with the service account credentials"""

    return "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"


@pytest.fixture
def asset_france(gee_dir, scope="session"):
    """return the france asset available in our test account"""

    return f"{gee_dir}/france"


@pytest.fixture
def asset_italy(gee_dir, scope="session"):
    """return the italy asset available in our test account"""

    return f"{gee_dir}/italy"


@pytest.fixture
def asset_table_aoi(gee_dir, scope="session"):
    """return the aoi for the reclassify tests available in our test account"""

    return f"{gee_dir}/reclassify_table_aoi"


@pytest.fixture
def asset_image_aoi(gee_dir, scope="session"):
    """return the aoi for the reclassify tests available in our test account"""

    return f"{gee_dir}/reclassify_image_aoi"


@pytest.fixture
def no_name(scope="session"):
    """return a no-name tuple"""

    return ("no_name", "#000000")


@pytest.fixture
def alert():
    """return a dummy alert that can be used everywhere to display informations"""

    return sw.Alert()


@pytest.fixture
def readme(root_dir, scope="session"):
    """return the readme file path"""

    return root_dir / "README.rst"


@pytest.fixture
def asset_description(scope="session"):
    """return a test asset name"""

    return "test_travis"


@pytest.fixture
def asset_id(asset_description, scope="session"):
    """return a test asset id"""

    return f"users/bornToBeAlive/sepal_ui_test/{asset_description}"
