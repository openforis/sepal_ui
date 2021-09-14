import pytest

import ee

from sepal_ui import aoi
from sepal_ui.mapping import SepalMap
from sepal_ui.message import ms


class TestAoiView:

    FOLDER = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"

    def test_init(self):

        # default init
        view = aoi.AoiView(folder=self.FOLDER)
        assert isinstance(view, aoi.AoiView)

        # init without ee
        view = aoi.AoiView(gee=False)
        assert view.model.ee == False

        # init with ADMIN
        view = aoi.AoiView("ADMIN")
        assert {"header": "CUSTOM"} not in view.w_method.items

        # init with CUSTOM
        view = aoi.AoiView("CUSTOM")
        assert {"header": "ADMIN"} not in view.w_method.items

        # init with a list
        view = aoi.AoiView(["POINTS"])
        assert {"text": ms.aoi_sel.points, "value": "POINTS"} in view.w_method.items
        assert len(view.w_method.items) == 1 + 1  # 1 for the header, 1 for the object

        # init with a remove list
        view = aoi.AoiView(["-POINTS"])
        assert {"text": ms.aoi_sel.points, "value": "POINTS"} not in view.w_method.items
        assert (
            len(view.w_method.items) == len(aoi.AoiModel.METHODS) + 2 - 1
        )  # 2 headers this time

        # init with a mix of both
        with pytest.raises(Exception):
            view = aoi.AoiView(["-POINTS", "DRAW"])

        # init with a non existing keyword
        with pytest.raises(Exception):
            view = aoi.AoiView(["TOTO"])

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

        # test the cascade of the admin selector
        view = aoi.AoiView(gee=False)
        view.w_method.v_model = "ADMIN2"

        view.w_admin_0.v_model = view.w_admin_0.items[0]["value"]
        assert len(view.w_admin_1.items)

        view.w_admin_1.v_model = view.w_admin_1.items[0]["value"]
        assert len(view.w_admin_2.items)

        return

    def test_update_aoi(self):

        # init with a map
        m = SepalMap(dc=True)
        view = aoi.AoiView(map_=m, gee=False)

        # select Italy
        item = next(i for i in view.w_admin_0.items if i["text"] == "Italy")
        view.w_method.v_model = "ADMIN0"
        view.w_admin_0.v_model = item["value"]

        # launch the update
        view._update_aoi(None, None, None)

        # perform checks
        assert view.updated == 1
        assert view.model.name == "ITA"
        assert len(view.map_.layers) == 2

        # same with GEE
        m = SepalMap(dc=True)
        view = aoi.AoiView(map_=m, folder=self.FOLDER)

        # select Italy
        item = next(i for i in view.w_admin_0.items if i["text"] == "Italy")
        view.w_method.v_model = "ADMIN0"
        view.w_admin_0.v_model = item["value"]

        # launch the update
        view._update_aoi(None, None, None)

        # perform checks
        assert view.updated == 1
        assert view.model.name == "ITA"
        assert len(view.map_.layers) == 2

        return

    def test_reset(self):

        # select a model
        m = SepalMap(dc=True)
        view = aoi.AoiView(map_=m, folder=self.FOLDER)

        # select Italy
        item = next(i for i in view.w_admin_0.items if i["text"] == "Italy")
        view.w_method.v_model == "ADMIN0"
        view.w_admin_0.v_model = item["value"]

        # launch the update
        view._update_aoi(None, None, None)

        # reset
        view.reset()

        # checks
        assert len(view.map_.layers) == 1
        assert view.w_method.v_model == None
        assert view.model.name == None

        return

    def test_polygonize(self):

        src_json = {
            "properties": {"style": {"radius": 1000}},  # 1 km
            "geometry": {"coordinates": [0, 0]},
        }

        dst_json = {
            "properties": {"style": {"radius": 1000}},
            "geometry": {
                "type": "Polygon",
                "coordinates": (
                    (
                        (0.008983152841195215, 0.0),
                        (0.008939896504919428, -0.0008805029526026642),
                        (0.008810544078256724, -0.0017525261802355968),
                        (0.008596341295787095, -0.002607671622333609),
                        (0.008299351047400873, -0.0034377037606662187),
                        (0.007922433511541403, -0.004234628931893385),
                        (0.007469218610123095, -0.004990772310922396),
                        (0.006944071050399075, -0.005698851823673321),
                        (0.006352048290444342, -0.006352048277432306),
                        (0.005698851833069822, -0.0069440710333991814),
                        (0.004990772317233534, -0.007469218588967309),
                        (0.004234628935748622, -0.007922433486296168),
                        (0.003437703762728802, -0.008299351018378295),
                        (0.0026076716232338705, -0.008596341263535997),
                        (0.0017525261805088842, -0.008810544043534168),
                        (0.0008805029526373357, -0.008939896468644966),
                        (1.4512683833891605e-17, -0.008983152804391653),
                        (-0.000880502952637307, -0.00893989646864497),
                        (-0.0017525261805088558, -0.008810544043534175),
                        (-0.0026076716232338428, -0.008596341263536006),
                        (-0.0034377037627287754, -0.008299351018378306),
                        (-0.004234628935748596, -0.007922433486296182),
                        (-0.004990772317233511, -0.007469218588967324),
                        (-0.0056988518330698, -0.006944071033399198),
                        (-0.006352048290444325, -0.006352048277432324),
                        (-0.006944071050399062, -0.005698851823673338),
                        (-0.007469218610123084, -0.004990772310922415),
                        (-0.007922433511541394, -0.004234628931893402),
                        (-0.008299351047400866, -0.003437703760666234),
                        (-0.00859634129578709, -0.0026076716223336228),
                        (-0.008810544078256722, -0.0017525261802356091),
                        (-0.008939896504919427, -0.0008805029526026751),
                        (-0.008983152841195215, -9.078761431739572e-18),
                        (-0.008939896504919428, 0.0008805029526026568),
                        (-0.008810544078256726, 0.0017525261802355913),
                        (-0.008596341295787097, 0.0026076716223336054),
                        (-0.008299351047400873, 0.0034377037606662174),
                        (-0.007922433511541403, 0.004234628931893386),
                        (-0.007469218610123095, 0.004990772310922399),
                        (-0.006944071050399072, 0.005698851823673324),
                        (-0.006352048290444338, 0.006352048277432312),
                        (-0.005698851833069819, 0.006944071033399185),
                        (-0.004990772317233533, 0.00746921858896731),
                        (-0.0042346289357486225, 0.007922433486296168),
                        (-0.003437703762728805, 0.008299351018378294),
                        (-0.002607671623233875, 0.008596341263535997),
                        (-0.0017525261805088912, 0.008810544043534168),
                        (-0.0008805029526373448, 0.008939896468644966),
                        (-2.558610588923554e-17, 0.008983152804391653),
                        (0.0008805029526372937, 0.008939896468644971),
                        (0.0017525261805088406, 0.008810544043534178),
                        (0.002607671623233826, 0.008596341263536011),
                        (0.0034377037627287576, 0.008299351018378314),
                        (0.004234628935748577, 0.00792243348629619),
                        (0.0049907723172334904, 0.007469218588967338),
                        (0.005698851833069779, 0.006944071033399217),
                        (0.006352048290444301, 0.006352048277432348),
                        (0.006944071050399037, 0.005698851823673367),
                        (0.007469218610123062, 0.004990772310922448),
                        (0.007922433511541373, 0.004234628931893442),
                        (0.008299351047400847, 0.0034377037606662794),
                        (0.008596341295787074, 0.0026076716223336735),
                        (0.00881054407825671, 0.001752526180235665),
                        (0.008939896504919422, 0.0008805029526027359),
                        (0.008983152841195215, 7.400802032440134e-17),
                        (0.008983152841195215, 0.0),
                    ),
                ),
            },
        }

        # check the transformation
        assert aoi.AoiView.polygonize(src_json) == dst_json

        return
