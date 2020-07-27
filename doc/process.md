# Create a process Tile

Using the sepal_ui framework, you'll be able to create a tile that can interface with any of your process. 

## Code 

```py
from sepal_ui import widgetFactory as wf
from sepal_ui import widgetBinding as wb

#use a class to define your input and output in order to have mutable variables
class Process:
    def __init__(self):
        #set up your inputs
        self.slider_value = None
        self.text_value = None
    
        #set up your output
        self.link = None
process_io = Process()
```

Unlike the two other Tile type available in the framework. We haver decided to let the user free fo the creation of a process tile. You' need to create manually all the component that will be included in your process tile. A list of the available component of the framework can be found [here](.components#sepal_ui) as well as a [non-exhaustive list](.components#ipyvuetify) of the useful `ipyvuetify` inputs.

```py
#create the output alert 
process_output = wf.OutputWidget()

#create the button that start your process
process_btn = wf.ProcessBtn('Click me')

#create the widgets following ipyvuetify requirements 
process_slider = v.Slider(label= 'slider', class_="mt-5", thumb_label='always', v_model=0)
process_text = v.TextField(label='Write text', v_model=None)

process_inputs = [process_slider, process_text]

#bind the widget to the inputs
wb.bind(process_slider, process_io, 'slider_value', process_output)
wb.bind(process_text, process_io, 'text_value', process_output

#create a process tile
id_ = "process_widget"
title = 'Process'

fao_process = wf.Tile(id_, title, btn=process_btn, inputs=process_inputs, output=process
```


using the `wb.bind` function you can bind the widget to your `Process_io` object.

```py
#bind the button to the process by writing a custom function
from scripts import process
from sepal_ui.sepal_ui.scripts import utils

def process_start(widget, event, data, output):
    
    global fao_results
    
    #toggle the loading button
    utils.toggleLoading(widget)
    #launch any process you want
    process_io.link = process.run_my_process(
        output, 
        percentage=process_io.slider_value, 
        name=process_io.text_value
    )
    
    #toggle the loading button
    utils.toggleLoading(widget)

process_btn.on_event('click', partial(process_start, output=process_output))

#this tiles will only be displayed if you launch voila from this file 
fao_process
```

for more usage example, please go to [sepal_ui_fake_app](https://github.com/12rambau/sepal_ui_template)

---
[ go to  &rarr; readme.md](../README.md) 

