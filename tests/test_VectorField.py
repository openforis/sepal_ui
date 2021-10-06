from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

import pandas as pd
import pytest

from sepal_ui import sepalwidgets as sw


class TestVectorField:
    def test_init(self, vector_field):

        assert isinstance(vector_field, sw.VectorField)

        return

    def test_update_file(self, vector_field, fake_vector):

        # change the value of the file
        vector_field._update_file({"new": str(fake_vector)})

        test_data = {
            "pathname": str(fake_vector),
            "column": "ALL",
            "value": None,
        }

        assert vector_field.v_model == test_data

        # change for a empty file
        vector_field._update_file({"new": None})
        assert vector_field.v_model == vector_field.default_v_model

        return

    def test_reset(self, vector_field, fake_vector):

        # change the value of the file
        vector_field._update_file({"new": str(fake_vector)})

        # reset the loadtable
        vector_field.reset()

        # assert the current values
        assert vector_field.v_model == vector_field.default_v_model

        return

    def test_update_column(self, vector_field, fake_vector):

        # change the value of the file
        vector_field._update_file({"new": str(fake_vector)})

        # read a column
        vector_field.w_column.v_model = "GID_0"  # first one to select
        assert vector_field.v_model["column"] == "GID_0"
        assert "d-none" not in vector_field.w_value.class_
        assert vector_field.w_value.items == ["VAT"]

        return

    def test_update_value(self, vector_field, fake_vector):

        # change the value of the file
        vector_field._update_file({"new": str(fake_vector)})

        # read a column
        vector_field.w_column.v_model = "GID_0"  # first one to select
        vector_field.w_value.v_model = "VAT"  # unique possible value

        assert vector_field.v_model["value"] == "VAT"

        return

    @pytest.fixture
    def vector_field(self):
        """return a VectorField"""

        return sw.VectorField()

    @pytest.fixture
    def fake_vector(self, tmp_dir):
        """return a fake vector based on the vatican file"""

        file = tmp_dir / "test.zip"

        gadm_vat_link = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_VAT_shp.zip"
        name = "gadm36_VAT_0"

        # download vatican city from GADM
        urlretrieve(gadm_vat_link, file)

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        file.unlink()

        yield tmp_dir / f"{name}.shp"

        # delete the files
        [f.unlink() for f in tmp_dir.glob(f"{name}.*")]

        return
