"""ResizeTrigger is an essential object of sepal-ui.

It guarantees that the maps displayed in the application are allways resized when you change the view. Without it moving from one panel to another would make some of the map tile invisible.
"""

from pathlib import Path

import ipyvuetify as v
from IPython.display import display
from traitlets import Unicode


class ResizeTrigger(v.VuetifyTemplate):
    """A trigger to resize maps when a change of display is done.

    Every time resize is called, the javascript resize event is trigger of the application.
    """

    # load the js file
    js = (Path(__file__).parent / "js/jupyter_resize.js").read_text()
    template = Unicode("<script>{methods: {jupyter_resize(){%s}}}</script>" % js).tag(
        sync=True
    )
    "Unicode: the javascript script to manually trigger the resize event"

    def resize(self):
        """trigger the template method i.e. the resize event."""
        return self.send({"method": "resize"})


# create one single resizetrigger that will be used as a singleton everywhere
# singletons are bad but if we display multiple instances of rt for every DrawItem
# the initial offset will be impossible to manage
rt = ResizeTrigger()
display(rt)
