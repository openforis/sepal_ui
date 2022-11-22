from ipyleaflet import TileLayer
from sepal_ui import mapping as sm


class TestBasemaps:
    def test_get_xyz_dict(self):

        # Retrieve 4 random maps
        random_basemaps = [
            "Esri.OceanBasemap",
            "HikeBike.HikeBike",
            "HikeBike.HillShading",
            "BasemapAT.orthofoto",
        ]
        basemaps = sm.basemaps.get_xyz_dict()
        assert all([m in basemaps for m in random_basemaps])

        return

    def test_xyz_to_leaflet(self):

        # Retrieve 1 random maps + the five manually added
        random_basemaps = [
            "Esri.OceanBasemap",
            "OpenStreetMap",
            "ROADMAP",
            "SATELLITE",
            "TERRAIN",
            "HYBRID",
        ]
        basemaps = sm.basemaps.xyz_to_leaflet()
        assert all([m in basemaps for m in random_basemaps])

        for tile in basemaps.values():
            assert isinstance(tile, TileLayer)

        return
