import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestAppBar:
    def test_init(self):

        # default init
        appBar = sw.AppBar()

        assert isinstance(appBar, sw.AppBar)
        assert isinstance(appBar.toggle_button, v.Btn)
        assert isinstance(appBar.children[1], v.ToolbarTitle)
        assert appBar.children[1].children[0] == "SEPAL module"

        # exhaustive
        title = "toto"
        appBar = sw.AppBar(title)
        assert appBar.children[1].children[0] == title

        return

    def test_title(self):

        appBar = sw.AppBar()
        title = "toto"
        res = appBar.set_title(title)

        assert res == appBar
        assert appBar.children[1].children[0] == title

        return


if __name__ == "__main__":
    unittest.main()
