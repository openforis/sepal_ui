from IPython.display import display
import ipyvuetify as v
from traitlets import Unicode


class ResizeTrigger(v.VuetifyTemplate):
    """
    A trigger to resize maps when a change of display is done.
    Every time resize is called, the javascript resize event is trigger of the application
    """

    template = Unicode(
        """
        <script>
            {methods: {
                jupyter_resize(){
                    window.dispatchEvent(new Event('resize'));
                }
            }}
        </script>
    """
    ).tag(sync=True)
    "Unicode: the javascript script to manually trigger the resize event"

    def resize(self):
        """trigger the template method i.e. the resize event"""

        self.send({"method": "resize"})

        return


# create one single resizetrigger that will be used as a singleton everywhere
# singletons are bad but if we display multiple instances of rt for every DrawItem
# the initial offset will be impossible to manage
rt = ResizeTrigger()
display(rt)
