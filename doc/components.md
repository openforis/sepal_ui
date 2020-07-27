# Components

## Sepal_ui

### Widgets

```py
from sepal_ui import widgetFactory as wf

wf.AppBar(title='SEPAL module')

wf.DrawerItem(title, icon=None, card='', href='')

wf.NavDrawer(items, code = False, wiki = False, issue = None)

wf.Footer (text='SEPAL \u00A9 2020')

wf.App (tiles=[''], appBar=None, footer=None, navDrawer=None)

wf.Tile(id_, title, inputs=[''], btn=None, output=None)

wf.TileAbout(pathname)

wf.DownloadBtn(text, url="#")

wf.ProcessBtn(text="Launch process")

wf.TileAOI(io)

wf.Aoi_IO()

wf.OutputWidget(text='Click it')

```

### functions 
```py
from sepal_ui import widgetFactory as wf
from sepal_ui import widgetBinding as wb
from sepal_ui.scripts import utils

wf.hideCards(tileId, tiles)

wb.displayDrawer(drawer, toggleButton)

wb.display_tile(item, tiles)

wb.bind(widget, obj, variable, output=None, output_message='The selected variable is: ')

wb.toggle_inputs(input_list, widget_list)

utils.displayIO(widget_alert, message, alert_type='info')

utils.toggleLoading(btn)
```

Run `help(__func__)`to get more information on each function 

## Ipyvuetify

```py 
import ipyvuetify as v

v.Alert(
    children=['message'], 
    type='info', text=True, 
    class_="mt-5"
)

v.TextField(
    label='label', 
    v_model=None,
    class_='d-inline'
)

v.Select(
    items=[elts], 
    label='label', 
    v_model=None,
    class_='d-inline'
)

v.Slider(
    label= 'slider', 
    class_="mt-5 d-inline", 
    thumb_label='always', 
    v_model=0
)

v.Btn(
    class_='ma-2',
    xs5=True,
    color='success',
    href=url,
    children=[
        v.Icon(left=True, children=['mdi-download']),
        text
    ]
)
```

they all can be bind with the `wb.bind` function or with `widget.on_event('change', callback)`.



