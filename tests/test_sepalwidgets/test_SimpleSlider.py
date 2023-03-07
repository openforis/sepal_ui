"""Test the SimpleSlider widget"""

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """test that the widgtet is created and have the custom class"""

    w = sw.SimpleSlider()

    assert isinstance(w, v.Slider)
    assert isinstance(w, sw.SimpleSlider)
    assert "v-no-messages" in w.class_

    return
