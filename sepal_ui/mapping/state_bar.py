from traitlets import Int, observe

from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms


class StateBar(sw.StateBar):
    """
    A specific statebar dedicated to the the counting of loading tiles in the map
    """

    nb_layer = Int(0).tag(sync=True)
    "Int: the number of layers in the map"

    nb_loading_layer = Int(0).tag(sync=True)
    "Int: the number of loading layer in the map"

    def loading_change(self, change):
        """update the nb_layer_loading trait according to layer loading state"""

        if change["new"]:
            self.nb_loading_layer += 1
        else:
            self.nb_loading_layer -= 1

        return

    @observe("nb_loading_layer", "nb_layer")
    def _update_state(self, change):

        # check if anything is loading
        self.loading = bool(self.nb_loading_layer)

        # update the message
        if self.loading:
            msg = ms.mapping.loading_layers.format(self.nb_loading_layer, self.nb_layer)
        else:
            msg = ms.mapping.loading_complete.format(self.nb_layer)

        self.msg = msg

        return
