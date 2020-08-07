from functools import partial

import ipyvuetify as v
import geemap
import ee

from sepal_ui.scripts import utils, run_aoi_selection, mapping
 

ee.Initialize()

#make the toolbar button clickable 
def displayDrawer(drawer, toggleButton):
    """
    bin the drawer to it's toggleButton
    
    Args:
        drawer (v.navigationDrawer) : the drawer tobe displayed
        toggleButton(v.Btn) : the button that activate the drawer
    """
    def on_click(widget, event, data, drawer):
        drawer.v_model = not drawer.v_model
        
    toggleButton.on_event('click', partial(on_click, drawer=drawer))

#display the appropriate tile
def display_tile(item, tiles):
    """
    display the apropriate tiles when the item is clicked
    
    Args:
        item (v.ListItem) : the item in the drawer that select the active tile
        tiles ([v.Layout]) : the list of all the available tiles in the app
    """
    def on_click(widget, event, data, tiles):
        for tile in tiles:
            if widget._metadata['card_id'] == tile._metadata['mount_id']:
                tile.class_="ma-5 d-inline"
            else:
                tile.class_="ma-5 d-none"
    
    item.on_event('click', partial(on_click, tiles=tiles))

def bind(widget, obj, variable, output=None, output_message='The selected variable is: '):
    """ 
    bind the variable to the widget
    
    Args:
        widget (v.XX) : an ipyvuetify input element
        obj : the process_io object
        variable (str) : the name of the member in process_io object
        output (v.Alert, opotional) : the alert element to display the variable new value
        output_message (str, optionnal) : the output message before the variable display
    """
    
    def on_change(widget, event, data, obj, variable, output, output_message):
        
        setattr(obj, variable, widget.v_model)
        if output:
            message = output_message + str(widget.v_model)
            utils.displayIO(output, message)
        
    widget.on_event('change', partial(
        on_change,
        obj=obj,
        variable=variable, 
        output=output, 
        output_message=output_message
    ))
    
def toggle_inputs(input_list, widget_list):
    """
    display only the widgets that are part of the input_list. the widget_list is the list of all the widgets of the tile.
    
    Args:
        input_list ([v.widget]) : the list of input to be display
        widget_list ([v.widget]) : the list of the tile widget
    """
    
    for input_item in widget_list:
        if input_item in input_list:
            input_item.class_ = 'd-inline'
        else:
            input_item.class_ = 'd-none'

    return

def bindAoiMethod(method_widget, list_input, obj, m, dc, selection_method):
    """
    change the display of the AOI selector according to the method selected. will only display the useful one
    
    Args: 
        method_widget (v.select) : the method selector widget 
        list_input ([v.widget]) : the list of all the aoi inputs
        obj (Aoi_IO) : the IO object of the tile
        m (geemap.Map) the map displayed in the tile
        dc (DrawControl) : the drawing control
        selection_method ([str]) : the available selection methods
    """
    
    def on_change(widget, event, data, list_input, obj, m, dc, selection_method):
        
        #clearly identify the differents widgets 
        aoi_file_input = list_input[0]
        aoi_file_name = list_input[1]
        aoi_country_selection = list_input[2]
        aoi_asset_name = list_input[3]
        
        setattr(obj, 'selection_method', widget.v_model)
        
        #remove the map 
        try:
            m.remove_control(dc)
        except:
            pass
        dc.clear()
        #toogle the appropriate inputs
        if widget.v_model == selection_method[0]: #country selection
            toggle_inputs([aoi_country_selection], list_input)
        elif widget.v_model == selection_method[1]: #drawing
            toggle_inputs([aoi_file_name], list_input)
            m.add_control(dc)
        elif widget.v_model == selection_method[2]: #shp file
            toggle_inputs([aoi_file_input], list_input)
        elif widget.v_model == selection_method[3]: #gee asset
            toggle_inputs([aoi_asset_name], list_input)
    
    
    
    method_widget.on_event('change', partial(
        on_change,
        list_input=list_input,
        obj=obj,
        m=m,
        dc=dc, 
        selection_method=selection_method
    ))
    
    return 

# Handle draw events
def handle_draw(dc, obj, variable, output=None):
    """ 
    handle the drawing of a geometry on a map. The geometry is transform into a ee.featurecollection and send to the variable attribute of obj.
    
    Args: 
        dc (DrawControl) : the draw control on which the drawing will be done 
        obj (obj IO) : any object created for IO of your tile 
        variable (str) : the name of the atrribute of the obj object where to store the ee.FeatureCollection 
        output (v.Alert, optionnal) : the output to display results
        
    """
    def on_draw(self, action, geo_json, obj, variable, output):
        geom = geemap.geojson_to_ee(geo_json, False)
        feature = ee.Feature(geom)
        setattr(obj, variable, ee.FeatureCollection(feature)) 
        
        if output:
            utils.displayIO(output, 'A shape have been drawn')
        
        return 
        
        
    dc.on_draw(partial(
        on_draw,
        obj=obj,
        variable=variable,
        output=output
    ))
    
    return

def bindAoiProcess(btn, io, m, dc, output, list_method):
    """
    Create an asset in your gee acount and serve it to the map.
    
    Args:
        btn (v.Btn) : the btn that launch the process
        io (Aoi_IO) : the IO of the aoi selection tile
        m (geemap.Map) : the tile map
        dc (drawcontrol) : the drawcontrol
        output (v.Alert) : the alert of the selector tile
        list_method([str]) : the list of the available selections methods
    """
    
    def on_click(widget, event, data, io, m, dc, output, list_method):
        
        utils.toggleLoading(widget)
        
        #create the aoi asset
        assetId = run_aoi_selection.run_aoi_selection(
            file_input        = io.file_input, 
            file_name         = io.file_name, 
            country_selection = io.country_selection, 
            asset_name        = io.assetId, 
            drawn_feat        = io.drawn_feat,
            drawing_method    = io.selection_method,
            widget_alert      = output, 
            list_method       = list_method, 
        )
        
        #remove the dc
        dc.clear()
        try:
            m.remove_control(dc)
        except:
            pass
        
        #display it on the map
        if assetId:
            mapping.update_map(m, dc, assetId)
            
        utils.toggleLoading(widget)
        
        #add the value to the IO object 
        setattr(io, 'assetId', assetId)
        
        return 
    
    btn.on_event('click', partial(
        on_click,
        io          = io, 
        m           = m, 
        dc          = dc, 
        output      = output,
        list_method = list_method
    ))
    
    return

def checkInput(input_, output=None, output_message=None):
    """
    Check if the inpupt value is initialised return false if not and display an error message
    
    Args:
        input_ : the input to check
        output (v.Alert, optional): the output where we write the message
        output_message (str, optionnal): the message to display if the input is not set
        
    Returns:
        (bool): check if the value is initialized
    """
    default_message = "The value has not been initialized"
    init = True 
    
    if input_ == None:
        init = False
        if output:
            message = output_message if output_message else output_message
            utils.displayIO(output, message, 'error')
    
    return init
            