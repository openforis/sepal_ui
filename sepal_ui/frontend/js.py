import ipyvuetify as v 
import traitlets
from IPython.display import display

class ResizeTrigger(v.VuetifyTemplate):
    template = traitlets.Unicode('''
    <template>
    </template>
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
    
    
    resize = traitlets.Int(0).tag(sync=True)
    
rt = ResizeTrigger()
_ = display(rt)