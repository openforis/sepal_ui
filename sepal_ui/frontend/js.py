import ipyvuetify as v 
from traitlets import Int, Unicode
from IPython.display import display

class ResizeTrigger(v.VuetifyTemplate):
    template = Unicode('''
    <script>
        modules.export = {
            watch: {
                resize() {
                    window.dispatchEvent(new Event('resize'));
                }
            }
        }
        </script>
    ''').tag(sync=True)
    
    resize = Int(0).tag(sync=True)

rt = ResizeTrigger()
display(rt)
