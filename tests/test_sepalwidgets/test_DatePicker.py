"""Test the DatePicker widget."""

from traitlets import Any

from sepal_ui import sepalwidgets as sw
from sepal_ui.model import Model


def test_init() -> None:
    """Check widget init."""
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


def test_kwargs() -> None:
    """Test kwargs to both datepicker and layout."""
    date_picker_kwargs = {
        "min": "2018-02-14",
        "max": "2021-03-14",
    }

    layout_kwargs = {
        "class_": "pa-0",
        "align_center": False,
    }

    datepicker = sw.DatePicker(
        v_model="", layout_kwargs=layout_kwargs, **date_picker_kwargs
    )

    assert datepicker.date_picker.min == "2018-02-14"
    assert datepicker.date_picker.max == "2021-03-14"
    assert datepicker.class_ == "pa-0"
    assert datepicker.align_center is False

    return


def test_bind() -> None:
    """Check we can bind the value with other trait."""
    datepicker = sw.DatePicker()

    class Test_io(Model):
        out = Any(None).tag(sync=True)

    test_io = Test_io()

    test_io.bind(datepicker, "out")

    date = "2020-06-12"
    datepicker.v_model = date

    assert test_io.out == date
    assert datepicker.menu.v_model is False

    return


def test_disable() -> None:
    """Check the widget can be disabled."""
    datepicker = sw.DatePicker()

    for boolean in [True, False]:
        datepicker.disabled = boolean
        assert datepicker.menu.v_slots[0]["children"].disabled == boolean

    return


def test_is_valid_date() -> None:
    """Ensure v_model can only be a well defined date."""
    datepicker = sw.DatePicker()

    # a nicely shaped date
    test = "2022-03-14"
    assert datepicker.is_valid_date(test) is True

    # a badly shaped date
    test = "2022-50-14"
    assert datepicker.is_valid_date(test) is False

    return


def test_check_date() -> None:
    """Check when the date is manually set, the date format is tested as well."""
    datepicker = sw.DatePicker()

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
