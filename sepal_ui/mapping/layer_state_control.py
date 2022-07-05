from traitlets import Int, observe
from ipyleaflet import WidgetControl

from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms


class LayerStateControl(WidgetControl):
    """
    A specific statebar dedicated to the the counting of loading tiles in the map

    every time a map is added to the map the counter will be raised by one. same behaviour with removed.
    """

    nb_layer = Int(0).tag(sync=True)
    "Int: the number of layers in the map"

    nb_loading_layer = Int(0).tag(sync=True)
    "Int: the number of loading layer in the map"

    def __init__(self, m, **kwargs):

        # save the map as a member of the widget
        self.m = m

        # create a statebar
        msg = ms.layer_state.complete.format(self.nb_layer)
        self.w_state = sw.StateBar(loading=False, msg=msg)

        # overwrite the widget set in the kwargs (if any)
        kwargs["widget"] = self.w_state
        kwargs["position"] = kwargs.pop("position", "topleft")
        kwargs["transparent_bg"] = True

        # create the widget
        super().__init__(**kwargs)

        # add js behaviour
        self.m.observe(self.update_nb_layer, "layers")

    def update_nb_layer(self, change):
        """
        Update the number of layer monitored by the statebar
        """

        # exit if nothing changed
        if len(change["new"]) == len(change["old"]):
            return

        self.nb_layer = len([lyr for lyr in change["new"] if not lyr.base])

        # identify the modified layer
        modified_layer = list(set(change["new"]) ^ set(change["old"]))[0]
        if modified_layer.base is True:
            return

        # add a layer
        if len(change["new"]) > len(change["old"]):
            modified_layer.observe(self.update_loading, "loading")

        # remove a layer
        elif len(change["new"]) < len(change["old"]) and modified_layer is True:
            self.nb_loading_layer += -1

        return

    def update_loading(self, change):
        """update the nb_loading_layer value according to the number of tile loading on the map"""

        increment = [-1, 1]
        self.nb_loading_layer += increment[change["new"]]

        return

    @observe("nb_loading_layer", "nb_layer")
    def _update_state(self, change):

        # check if anything is loading
        self.loading = bool(self.nb_loading_layer)

        # update the message
        if self.loading is True:
            msg = ms.layer_state.loading.format(self.nb_loading_layer, self.nb_layer)
        else:
            msg = ms.layer_state.complete.format(self.nb_layer)

        self.w_state.msg = msg

        return
