from pathlib import Path

import pandas as pd
import pytest

from sepal_ui import sepalwidgets as sw


class TestLoadTableField:
    def test_init(self, load_table):

        assert isinstance(load_table, sw.LoadTableField)

        return

    def test_on_file_input_change(self, load_table, fake_table, wrong_table):

        # change the value of the file
        load_table._on_file_input_change({"new": str(fake_table)})

        test_data = {
            "pathname": str(fake_table),
            "id_column": "id",
            "lng_column": "lng",
            "lat_column": "lat",
        }

        assert load_table.v_model == test_data

        # change for a empty update
        load_table._on_file_input_change({"new": None})
        assert load_table.v_model == load_table.default_v_model

        # test if the csv have not enough columns
        load_table._on_file_input_change({"new": str(wrong_table)})
        assert load_table.v_model == load_table.default_v_model
        assert load_table.fileInput.selected_file.error_messages != None

        return

    def test_reset(self, fake_table, load_table):

        # change the value of the file
        load_table._on_file_input_change({"new": str(fake_table)})

        # reset the loadtable
        load_table.reset()

        # assert the current values
        assert load_table.v_model == load_table.default_v_model

        return

    @pytest.fixture
    def load_table(self):
        """create a default load table"""

        return sw.LoadTableField()

    @pytest.fixture
    def fake_table(self, tmp_dir):
        """create a fake table"""

        filename = tmp_dir / "test.csv"

        end = 3

        coloseo = [1, 41.89042582290999, 12.492241627092199]
        fao = [2, 41.88369224629387, 12.489216069409004]
        columns = ["id", "lat", "lng"]
        df = pd.DataFrame([coloseo[:end], fao[:end]], columns=columns[:end])

        df.to_csv(filename, index=False)

        yield filename

        # delete the file
        filename.unlink()

        return

    @pytest.fixture
    def wrong_table(self, tmp_dir):
        """create a wrongly defined table (with 2 columns instead of the minimal 3"""

        filename = tmp_dir / "wrong_test.csv"

        end = 2

        coloseo = [1, 41.89042582290999, 12.492241627092199]
        fao = [2, 41.88369224629387, 12.489216069409004]
        columns = ["id", "lat", "lng"]
        df = pd.DataFrame([coloseo[:end], fao[:end]], columns=columns[:end])

        df.to_csv(filename, index=False)

        yield filename

        # delete the file
        filename.unlink()

        return
