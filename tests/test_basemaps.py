from sepal_ui import mapping as sm
from ipyleaflet import TileLayer


class TestBasemaps:
    def test_get_xyz_dict(self):

        assert len(sm.basemaps.get_xyz_dict()) == 123

        return

    def test_xyz_to_leaflet(self):

        assert len(sm.basemaps.xyz_to_leaflet()) == 128
        for tile in sm.basemaps.xyz_to_leaflet().values():
            assert isinstance(tile, TileLayer)

        return
