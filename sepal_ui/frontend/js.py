import ipyvuetify as v
from traitlets import Int, Unicode
from IPython.display import display


class ResizeTrigger(v.VuetifyTemplate):

    js_command = """ 
        <script>
            modules.export = {
                watch: {
                    resize() {
                        window.dispatchEvent(new Event('resize'));
                     }
                 }
             }
        </script>
    """

    js_command = "".join(js_command.split())

    template = Unicode(js_command).tag(sync=True)

    resize = Int(0).tag(sync=True)


rt = ResizeTrigger()
# display(rt)
