from sepal_ui import mapping as sm


class TestMapBtn:
    def test_map_btn(self):

        map_btn = sm.MapBtn("fas fa-folder")

        assert isinstance(map_btn, sm.MapBtn)

        return
