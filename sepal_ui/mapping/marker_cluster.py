"""Custom implementation of the marker cluster to hide it at once."""

from ipyleaflet import MarkerCluster
from traitlets import Bool, observe


class MarkerCluster(MarkerCluster):
    """Overwrite the MarkerCluster to hide all the underlying cluster at once.

    .. todo::
        remove when https://github.com/jupyter-widgets/ipyleaflet/issues/1108 is solved
    """

    visible = Bool(True).tag(sync=True)

    @observe("visible")
    def toggle_markers(self, change):
        """change the marker value according to the cluster viz."""
        for marker in self.markers:
            marker.visible = self.visible
