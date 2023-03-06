import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestSimpleSlider:
    def test_init(self) -> None:
        """test that the widgtet is created and have the custom class"""

        w = sw.SimpleSlider()

        assert isinstance(w, v.Slider)
        assert isinstance(w, sw.SimpleSlider)
        assert "v-no-messages" in w.class_

        return
