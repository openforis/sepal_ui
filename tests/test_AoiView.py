import ee

from sepal_ui import aoi
from sepal_ui.mapping import SepalMap
from sepal_ui.message import ms


class TestAoiTile:

    FOLDER = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"

    def test_init(self):

        # default init
        view = aoi.AoiView(folder=self.FOLDER)
        assert isinstance(view, aoi.AoiView)

        # init with ee
        view = aoi.AoiView(gee=False)
        assert view.model.ee == False

        # init with a map
        m = SepalMap(dc=True)
        view = aoi.AoiView(map_=m, folder=self.FOLDER)
        assert view.map_ == m

        return

    def test_admin(self):

        # test if admin0 is in Gaul
        view = aoi.AoiView(folder=self.FOLDER)
        first_gaul_item = {"text": "Abyei", "value": 102}
        assert first_gaul_item == view.w_admin_0.items[0]

        # test if admin0 is in gadm
        view = aoi.AoiView(gee=False, folder=self.FOLDER)
        first_gadm_item = {"text": "Afghanistan", "value": "AFG"}
        assert first_gadm_item == view.w_admin_0.items[0]

        return

    def test_activate(self):

        # test the activation of the widgets
        view = aoi.AoiView(folder=self.FOLDER)

        for method in aoi.AoiModel.METHODS:

            view.w_method.v_model = method

            for k, c in view.components.items():

                if k == method:
                    assert not "d-none" in c.class_
                elif hasattr(c, "parent"):
                    if view.components[k].parent == c:
                        assert not "d-none" in c.class_
                else:
                    assert "d-none" in c.class_

        return


if __name__ == "__main__":
    unittest.main()
