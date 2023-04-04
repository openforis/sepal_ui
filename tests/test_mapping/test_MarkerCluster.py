"""Test the MarkerCluster control."""
from ipyleaflet import Marker

from sepal_ui import mapping as sm


def test_init() -> None:
    """Init a MarkerCluster."""
    marker_cluster = sm.MarkerCluster()
    assert isinstance(marker_cluster, sm.MarkerCluster)

    return


def test_visible() -> None:
    """Hide MarkerCluster."""
    markers = [Marker(location=(0, 0)) for _ in range(3)]
    marker_cluster = sm.MarkerCluster(markers=markers)

    # check that the visibility trait is linked
    marker_cluster.visible = False
    assert all(m.visible is False for m in markers)
