from pathlib import Path

import pandas as pd

from sepal_ui import sepalwidgets as sw


class TestLoadTableField:
    def test_init(self):

        # init variables
        load_table = sw.LoadTableField()

        assert isinstance(load_table, sw.LoadTableField)

        return

    def test_on_file_input_change(self):

        # init var
        test_file = self._create_fake_table()
        load_table = sw.LoadTableField()

        # change the value of the file
        load_table._on_file_input_change({"new": str(test_file)})

        test_data = {
            "pathname": str(test_file),
            "id_column": "id",
            "lng_column": "lng",
            "lat_column": "lat",
        }

        assert load_table.v_model == test_data

        # delete the test file
        test_file.unlink()

        return

    def test_reset(self):

        # init var
        test_file = self._create_fake_table()
        load_table = sw.LoadTableField()

        # change the value of the file
        load_table._on_file_input_change({"new": str(test_file)})

        # reset the loadtable
        load_table.reset()

        # assert the current values
        assert load_table.v_model == load_table.default_v_model

        # delete the test file
        test_file.unlink()

        return

    def _create_fake_table(self):

        filename = Path.home() / "test.csv"

        coloseo = [1, 41.89042582290999, 12.492241627092199]
        fao = [2, 41.88369224629387, 12.489216069409004]
        df = pd.DataFrame([coloseo, fao], columns=["id", "lat", "lng"])

        df.to_csv(filename, index=False)

        return filename
