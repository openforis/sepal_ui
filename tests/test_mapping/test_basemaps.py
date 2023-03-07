"""Test the basemaps registered in the SepalMap."""

from ipyleaflet import TileLayer

from sepal_ui import mapping as sm


def test_get_xyz_dict() -> None:
    """Check some known basemaps and assert they are in the list."""
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


def test_xyz_to_leaflet() -> None:
    """Check the maps can be transformed in TileLayer."""
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
