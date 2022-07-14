from ipyleaflet import TileLayer

from sepal_ui import mapping as sm


class TestBasemaps:
    def test_get_xyz_dict(self):

        assert len(sm.basemaps.get_xyz_dict()) == 126

        return

    def test_xyz_to_leaflet(self):

        assert len(sm.basemaps.xyz_to_leaflet()) == 131
        for tile in sm.basemaps.xyz_to_leaflet().values():
            assert isinstance(tile, TileLayer)

        return
