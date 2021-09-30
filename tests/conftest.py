import geopandas as gpd
import pytest
from pathlib import Path
from zipfile import ZipFile
from urllib.request import urlretrieve

import sepal_ui.sepalwidgets as sw
from sepal_ui.aoi import AoiModel


@pytest.fixture
def dum_dir():
    """Creates a dummy directory"""

    dum_dir = Path("~").expanduser() / "tmp/sepal_ui_tests/"
    dum_dir.mkdir(exist_ok=True, parents=True)

    return dum_dir


@pytest.fixture
def aoi_model_gee(dum_dir):
    """Creates a default AOI GEE model using a default asset_id"""

    asset_id = "users/bornToBeAlive/sepal_ui_test/italy"

    return AoiModel(alert=sw.Alert(), folder=dum_dir, asset=asset_id)


@pytest.fixture
def aoi_model_local(dum_dir):
    """Creates a default AOI NOT-GEE model with a default vector"""

    # Get a dummy asset
    file = Path(gpd.datasets.get_path("nybb").replace("zip:", ""))
    vector = (dum_dir / "nybb").with_suffix(".shp")

    if not vector.exists():

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(dum_dir)

    return AoiModel(alert=sw.Alert(), folder=dum_dir, gee=False, vector=vector)
