import json

import pytest
from traitlets import Any

from sepal_ui import model


class TestModel:

    # prepare the data
    test_data = {"dummy1": "test1", "dummy2": "test2"}

    def test_export(self, dum_model):

        # create a fake model class with 2 traits
        dum_model.dummy1 = self.test_data["dummy1"]
        dum_model.dummy2 = self.test_data["dummy2"]

        dict_ = dum_model.export_data()

        # assert the result
        assert dict_ == self.test_data

        return

    def test_import(self, dum_model):

        # create a fake model class with 2 traits
        dum_model.import_data(self.test_data)

        # assert the result
        assert dum_model.dummy1 == self.test_data["dummy1"]
        assert dum_model.dummy2 == self.test_data["dummy2"]

        # create a fake model class using a str
        dum_model.import_data(json.dumps(self.test_data))

        # assert the result
        assert dum_model.dummy1 == self.test_data["dummy1"]
        assert dum_model.dummy2 == self.test_data["dummy2"]

        return

    def test_str(self, dum_model):

        # create a fake model class with 2 traits
        dum_model.import_data(self.test_data)

        assert str(dum_model) == "DummyClass(dummy1=test1, dummy2=test2)"

        return

    @pytest.fixture
    def dum_model(self):
        """return a dummy model with 2 traits, dummy1 and dummy2"""

        class DummyClass(model.Model):

            dummy1 = Any(None).tag(sync=True)
            dummy2 = Any(None).tag(sync=True)

        return DummyClass()
