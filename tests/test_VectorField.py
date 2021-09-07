from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import pandas as pd

from sepal_ui import sepalwidgets as sw


class TestVectorField:
    def test_init(self):

        # init variables
        load_table = sw.VectorField()

        assert isinstance(load_table, sw.VectorField)

        return

    def test_update_file(self):

        # init var
        test_file = self._create_fake_vector()
        load_vector = sw.VectorField()

        # change the value of the file
        load_vector._update_file({"new": test_file})

        test_data = {
            "pathname": test_file,
            "column": "ALL",
            "value": None,
        }

        assert load_vector.v_model == test_data

        # delete the test file
        for f in Path("~").expanduser().glob(f"{test_file.stem}.*"):
            f.unlink()

        return

    def test_reset(self):

        # init var
        test_file = self._create_fake_vector()
        load_vector = sw.VectorField()

        # change the value of the file
        load_vector._update_file({"new": test_file})

        # reset the loadtable
        load_vector.reset()

        # assert the current values
        assert load_vector.v_model == load_vector.default_v_model

        return

    def _create_fake_vector(self):

        # download vatican city from GADM
        root_dir = Path("~").expanduser()
        file = root_dir / "test.zip"

        gadm_vat_link = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_VAT_shp.zip"
        name = "gadm36_VAT_0"

        urlretrieve(gadm_vat_link, file)

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(root_dir)

        file.unlink()

        return root_dir / f"{name}.shp"
