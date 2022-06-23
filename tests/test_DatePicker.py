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

        # datepicker with default value
        value = "2022-03-14"
        datepicker = sw.DatePicker(v_model=value)
        assert datepicker.v_model == value

        return

    def test_bind(self, datepicker):
        class Test_io(Model):
            out = Any(None).tag(sync=True)

        test_io = Test_io()

        test_io.bind(datepicker, "out")

        date = "2020-06-12"
        datepicker.v_model = date

        assert test_io.out == date
        assert datepicker.menu.v_model is False

        return

    def test_disable(self, datepicker):

        for boolean in [True, False]:
            datepicker.disabled = boolean
            assert datepicker.menu.v_slots[0]["children"].disabled == boolean

        return

    def test_is_valid_date(self, datepicker):

        # a nicely shaped date
        test = "2022-03-14"
        assert datepicker.is_valid_date(test) is True

        # a badly shaped date
        test = "2022-50-14"
        assert datepicker.is_valid_date(test) is False

        return

    def test_check_date(self, datepicker):

        # manually update the value with a badely shaped date
        test = "2022-50-14"
        datepicker.v_model = test
        assert datepicker.v_model == test
        assert datepicker.date_text.error_messages is not None

        # manually update the value with a nicely shaped date
        test = "2022-03-14"
        datepicker.v_model = test
        assert datepicker.v_model == test
        assert datepicker.date_text.error_messages is None

        return

    @pytest.fixture
    def datepicker(self):
        """create a default datepicker"""

        return sw.DatePicker()
