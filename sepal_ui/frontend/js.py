from IPython.display import display
import ipyvuetify as v


class ResizeTrigger(v.VuetifyTemplate):
    def __init__(self):

        self.template = """
            <script>
                {methods: {
                    jupyter_resize(){
                        window.dispatchEvent(new Event('resize'));
                    }
                }}
            </script>
        """

        super().__init__()

    def resize(self):

        self.send({"method": "resize"})

        return


# create one single resizetrigger that will be used as a singleton everywhere
# singletons are bad but if we display multiple instances of rt for every DrawItem
# the initial offset will be impossible to manage
rt = ResizeTrigger()
display(rt)
