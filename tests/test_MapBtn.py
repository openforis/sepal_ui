import pytest

from sepal_ui import mapping as sm
from sepal_ui import sepalwidgets as sw


class TestMapBtn:
    def test_init(self):

        # check that the call with no kwargs still triger icon for no-regression
        map_btn = sm.MapBtn("fas fa-folder")
        assert isinstance(map_btn, sm.MapBtn)
        assert isinstance(map_btn.children[0], sw.Icon)
        assert map_btn.children[0].children[0] == "fas fa-folder"

        map_btn = sm.MapBtn(msg="to")
        assert isinstance(map_btn.children[0], str)
        assert map_btn.children[0] == "TO"

        map_btn = sm.MapBtn(msg="toto")
        assert isinstance(map_btn.children[0], str)
        assert map_btn.children[0] == "TOT"

        # check that text has priority
        map_btn = sm.MapBtn(logo="fas fa-folder", msg="toto")
        assert isinstance(map_btn.children[0], str)
        assert map_btn.children[0] == "TOT"

        # check error is raised when nothing is set
        with pytest.raises(
            ValueError, match="at least one of logo or msg need to be set"
        ):
            map_btn = sm.MapBtn()

        return
