from traitlets import Any
import json

from sepal_ui import model


class TestModel:

    # prepare the data
    test_data = {"dummy1": "test1", "dummy2": "test2"}

    def test_export(self):

        # create a fake model class with 2 traits
        dummy = self.DummyClass()
        dummy.dummy1 = self.test_data["dummy1"]
        dummy.dummy2 = self.test_data["dummy2"]

        dict_ = dummy.export_data()

        # assert the result
        assert dict_ == self.test_data

        return

    def test_import(self):

        # create a fake model class with 2 traits
        dummy = self.DummyClass()

        dummy.import_data(self.test_data)

        # assert the result
        assert dummy.dummy1 == self.test_data["dummy1"]
        assert dummy.dummy2 == self.test_data["dummy2"]

        # create a fake model class using a str
        dummy = self.DummyClass()
        dummy.import_data(json.dumps(self.test_data))

        # assert the result
        assert dummy.dummy1 == self.test_data["dummy1"]
        assert dummy.dummy2 == self.test_data["dummy2"]

        return

    def test_str(self):

        # create a fake model class with 2 traits
        dummy = self.DummyClass()
        dummy.import_data(self.test_data)

        assert str(dummy) == "DummyClass(dummy1=test1, dummy2=test2)"

        return

    class DummyClass(model.Model):
        """
        Dummy class wit 2 traits
        """

        dummy1 = Any(None).tag(sync=True)
        dummy2 = Any(None).tag(sync=True)
