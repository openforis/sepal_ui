import pytest

from traitlets import Any

from sepal_ui import sepalwidgets as sw
from sepal_ui.model import Model


class TestDatePicker:
    def test_init(self):

        # default init
        datepicker = sw.DatePicker()
        assert isinstance(datepicker, sw.DatePicker)

        # exhaustive
        datepicker = sw.DatePicker("toto")
        assert isinstance(datepicker, sw.DatePicker)

        return

    def test_bind(self, datepicker):
        class Test_io(Model):
            out = Any(None).tag(sync=True)

        test_io = Test_io()

        test_io.bind(datepicker, "out")

        date = "2020-06-12"
        datepicker.v_model = date

        assert test_io.out == date
        assert datepicker.menu.v_model == False

        return

    @pytest.fixture
    def datepicker(self):
        """create a default datepicker"""

        return sw.DatePicker()
