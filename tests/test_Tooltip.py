import pytest

from sepal_ui import sepalwidgets as sw


class TestStateBar:
    def test_init(self):

        # minimal tooltip on a btn
        btn = sw.Btn("click")
        tooltip = sw.Tooltip(widget=btn, tooltip="Click over the button")

        # assert that a slot cannot be modified
        with pytest.raises(Exception):
            tooltip.bottom = False

        return
