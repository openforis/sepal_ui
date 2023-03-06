from sepal_ui import sepalwidgets as sw


class TestRadio:
    def test_init(self):

        radio = sw.Radio()
        assert isinstance(radio, sw.Radio)
        assert "active" in radio.traits()
