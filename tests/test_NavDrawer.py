import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestNavDrawer:
    def test_init(self):

        items = [sw.DrawerItem("title {}".format(i)) for i in range(5)]

        # default init
        widget = sw.NavDrawer(items)
        assert isinstance(widget, sw.NavDrawer)
        assert widget.children[0].children == items

        # exhaustive
        code = "#code"
        wiki = "#wiki"
        issue = "#issue"

        # test all composition of links
        widget = sw.NavDrawer(items, code)
        assert len(widget.children[2].children) == 1
        assert widget.children[2].children[0].href == code

        widget = sw.NavDrawer(items, None, wiki)
        assert len(widget.children[2].children) == 1
        assert widget.children[2].children[0].href == wiki

        widget = sw.NavDrawer(items, None, None, issue)
        assert len(widget.children[2].children) == 1
        assert widget.children[2].children[0].href == issue

        widget = sw.NavDrawer(items, code, wiki)
        assert len(widget.children[2].children) == 2
        assert widget.children[2].children[0].href == code
        assert widget.children[2].children[1].href == wiki

        widget = sw.NavDrawer(items, None, wiki, issue)
        assert len(widget.children[2].children) == 2
        assert widget.children[2].children[0].href == wiki
        assert widget.children[2].children[1].href == issue

        widget = sw.NavDrawer(items, code, None, issue)
        len(widget.children[2].children) == 2
        widget.children[2].children[0].href == code
        widget.children[2].children[1].href == issue

        widget = sw.NavDrawer(items, code, wiki, issue)
        assert len(widget.children[2].children) == 3
        assert widget.children[2].children[0].href == code
        assert widget.children[2].children[1].href == wiki
        assert widget.children[2].children[2].href == issue

        return

    def test_display_drawer(self):

        # create the items
        nav_drawer = sw.NavDrawer()
        app_bar = sw.AppBar()

        previous = nav_drawer.v_model
        res = nav_drawer.display_drawer(app_bar.toggle_button)

        # fake the click
        _ = None
        nav_drawer._on_drawer_click(_, _, _)

        assert nav_drawer == res
        assert nav_drawer.v_model == (not previous)

        return

    def test_on_item_click(self):

        # create items
        items = [sw.DrawerItem(f"title {i}") for i in range(5)]
        nav_drawer = sw.NavDrawer(items)

        # activate the first one
        items[0].input_value = True
        for i in range(5):
            if i == 0:
                assert items[i].input_value == True
            else:
                assert items[i].input_value == False

        # activate the second one
        items[1].input_value = True
        for i in range(5):
            if i == 1:
                assert items[i].input_value == True
            else:
                assert items[i].input_value == False
