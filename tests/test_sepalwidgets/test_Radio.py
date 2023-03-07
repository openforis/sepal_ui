from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Init the radio widget"""
    radio = sw.Radio()
    assert isinstance(radio, sw.Radio)
    assert "active" in radio.traits()
