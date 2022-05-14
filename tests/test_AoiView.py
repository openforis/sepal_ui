import pytest

from sepal_ui import aoi
from sepal_ui.mapping import SepalMap
from sepal_ui.message import ms


class TestAoiView:
    def test_init(self, gee_dir):

        # default init
        view = aoi.AoiView(folder=gee_dir)
        assert isinstance(view, aoi.AoiView)

        # init without ee
        view = aoi.AoiView(gee=False)
        assert view.model.ee is False

        # init with ADMIN
        view = aoi.AoiView("ADMIN", folder=gee_dir)
        assert {"header": "CUSTOM"} not in view.w_method.items

        # init with CUSTOM
        view = aoi.AoiView("CUSTOM", folder=gee_dir)
        assert {"header": "ADMIN"} not in view.w_method.items

        # init with a list
        view = aoi.AoiView(["POINTS"], folder=gee_dir)
        assert {"text": ms.aoi_sel.points, "value": "POINTS"} in view.w_method.items
        assert len(view.w_method.items) == 1 + 1  # 1 for the header, 1 for the object

        # init with a remove list
        view = aoi.AoiView(["-POINTS"], folder=gee_dir)
        assert {"text": ms.aoi_sel.points, "value": "POINTS"} not in view.w_method.items
        assert (
            len(view.w_method.items) == len(aoi.AoiModel.METHODS) + 2 - 1
        )  # 2 headers this time

        # init with a mix of both
        with pytest.raises(Exception):
            view = aoi.AoiView(["-POINTS", "DRAW"], folder=gee_dir)

        # init with a non existing keyword
        with pytest.raises(Exception):
            view = aoi.AoiView(["TOTO"], folder=gee_dir)

        # init with a map
        m = SepalMap(dc=True)
        view = aoi.AoiView(map_=m, folder=gee_dir)
        assert view.map_ == m

        # test model name when using view
        view = aoi.AoiView(admin=100, folder=gee_dir)

        assert view.model.name == "GLP"

        return

    def test_admin(self, gee_dir):

        # test if admin0 is in Gaul
        view = aoi.AoiView(folder=gee_dir)
        first_gaul_item = {"text": "Abyei", "value": 102}
        assert first_gaul_item == view.w_admin_0.items[0]

        # test if admin0 is in gadm
        view = aoi.AoiView(gee=False)
        first_gadm_item = {"text": "Afghanistan", "value": "AFG"}
        assert first_gadm_item == view.w_admin_0.items[0]

        return

    def test_activate(self, aoi_gee_view):

        view = aoi_gee_view

        for method in aoi.AoiModel.METHODS:

            view.w_method.v_model = method

            for k, c in view.components.items():

                if k == method:
                    assert "d-none" not in c.class_
                elif hasattr(c, "parent"):
                    if view.components[k].parent == c:
                        assert "d-none" not in c.class_
                else:
                    assert "d-none" in c.class_

        # test the cascade of the admin selector
        view.w_method.v_model = "ADMIN2"

        view.w_admin_0.v_model = view.w_admin_0.items[0]["value"]
        assert len(view.w_admin_1.items)

        view.w_admin_1.v_model = view.w_admin_1.items[0]["value"]
        assert len(view.w_admin_2.items)

        return

    def test_update_aoi(self, aoi_gee_view, aoi_local_view):

        # select Italy
        item = next(i for i in aoi_gee_view.w_admin_0.items if i["text"] == "Italy")
        aoi_gee_view.w_method.v_model = "ADMIN0"
        aoi_gee_view.w_admin_0.v_model = item["value"]

        # launch the update
        aoi_gee_view._update_aoi(None, None, None)

        # perform checks
        assert aoi_gee_view.updated == 1
        assert aoi_gee_view.model.name == "ITA"
        assert len(aoi_gee_view.map_.layers) == 2

        # same without GEE

        # select Italy
        item = next(i for i in aoi_local_view.w_admin_0.items if i["text"] == "Italy")
        aoi_local_view.w_method.v_model = "ADMIN0"
        aoi_local_view.w_admin_0.v_model = item["value"]

        # launch the update
        aoi_local_view._update_aoi(None, None, None)

        # perform checks
        assert aoi_local_view.updated == 1
        assert aoi_local_view.model.name == "ITA"
        assert len(aoi_local_view.map_.layers) == 2

        return

    def test_reset(self, aoi_gee_view):

        # select Italy
        item = next(i for i in aoi_gee_view.w_admin_0.items if i["text"] == "Italy")
        aoi_gee_view.w_method.v_model = "ADMIN0"
        aoi_gee_view.w_admin_0.v_model = item["value"]

        # launch the update
        aoi_gee_view._update_aoi(None, None, None)

        # reset
        aoi_gee_view.reset()

        # checks
        assert len(aoi_gee_view.map_.layers) == 1
        assert aoi_gee_view.w_method.v_model is None
        assert aoi_gee_view.model.name is None

        return

    def test_polygonize(self):

        src_json = {
            "properties": {"style": {"radius": 1000}},  # 1 km
            "geometry": {"coordinates": [0, 0]},
        }

        # number of sides in the polygons
        # check this number instead of a regular output
        # because different geopandas versions give different results (7th decimal)

        # check the transformation
        dst_json = aoi.AoiView.polygonize(src_json)
        assert dst_json["geometry"]["type"] == "Polygon"
        assert len(dst_json["geometry"]["coordinates"][0]) == 65

        return

    @pytest.fixture
    def aoi_gee_view(self, gee_dir):
        """create an AoiView based on GEE with a silent sepalMap"""

        m = SepalMap(dc=True)
        return aoi.AoiView(map_=m, folder=gee_dir)

    @pytest.fixture
    def aoi_local_view(self, gee_dir):
        """create an AoiView based on GADM with a silent sepalMap"""

        m = SepalMap(dc=True)
        return aoi.AoiView(map_=m, gee=False)
