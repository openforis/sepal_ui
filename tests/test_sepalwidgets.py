import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestSepalWidgets:
    def test_generated(self) -> None:
        """test that all the vuetify classes have been overwritten."""
        # get all the classes names
        v_classes = [c for c in dir(v.generated) if c.startswith("__") is False]
        v_classes = [c for c in v_classes if c != "VuetifyWidget"]

        # set a class option
        option = "ma-5"

        for c in v_classes:

            if c in ["Alert", "Tooltip", "Banner", "DatePicker"]:
                # they are meant to be hidden by default
                # they are specific sepalwidgets and tested elswhere
                continue

            # test normal creation
            w = getattr(sw, c)(class_=option)

            assert w.viz is True
            assert w.class_ == option

            w.viz = False

            assert w.class_ == "d-none"
            assert w.viz is False
            assert w.old_class == option

            # test with extra sepalwidgets args
            w = getattr(sw, c)(class_=option, viz=False)

            assert w.class_ == "d-none"
            assert w.viz is False
            assert w.old_class == option

        return

    def test_html(self) -> None:
        """test a HTML class."""
        # set a class option
        option = "ma-5"

        w = sw.Html(tag="H1", children=["toto"], class_=option, viz=False)

        assert w.class_ == "d-none"
        assert w.viz is False
        assert w.old_class == option

        return
