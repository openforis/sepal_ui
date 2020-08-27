#!/usr/bin/env python3

from . import mapping
from . import sepalwidgets as sw
from . import widgetBinding as wb

import ee

ee.Initialize()



class Aoi_io:
    
    def __init__(self, alert_widget=None):
        """Initiate the Aoi object.

        Args:
            alert_widget (SepalAlert): Widget to display alerts.

        """

        # GEE parameters
        self.assetId = 'users/dafguerrerom/ReducedAreas_107PHU'
        self.column = None
        self.field = None
        self.selected_feature = None

        #set up your inputs
        self.file_input = None
        self.file_name = 'Manual_{0}'.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None
        self.alert = alert_widget
        
    def get_aoi_ee(self):

        """ Returns an ee.asset from self

        return: ee.Object

        """
        return ee.FeatureCollection(self.assetId)
    
    def get_columns(self):

        """ Retrieve the columns or variables from self

        return: sorted list cof column names
        """
        
        aoi_ee = self.get_aoi_ee()
        columns = ee.Feature(aoi_ee.first()).propertyNames().getInfo()
        columns = sorted([col for col in columns if col not in ['system:index', 'Shape_Area']])
        
        return columns
    
    def get_fields(self, column=None):
        """" Retrieve the fields from the selected self column
        
        Args:
            column (str) (optional): Used to query over the asset
        
        return: sorted list of fields

        """

        if not column:
            column = self.column

        aoi_ee = self.get_aoi_ee()
        fields = sorted(aoi_ee.distinct(column).aggregate_array(column).getInfo())

        return fields

    def get_selected_feature(self):
        """ Select a ee object based on the current state.

        Returns:
            ee.geometry

        """

        if not self.column or not self.field:
            self.alert.add_msg('error', f'You must first select a column and a field.')
            raise 

        ee_asset = self.get_aoi_ee()
        select_feature = ee_asset.filterMetadata(self.column, 'equals', self.field).geometry()

        # Specify the selected feature
        self.selected_feature = select_feature

        return select_feature

    def clear_selected(self):
        self.selected_feature = None

    def clear_attributes(self):

        # GEE parameters
        self.column = None
        self.field = None
        self.selected_feature = None

        #set up your inputs
        self.file_input = None
        self.file_name = 'Manual_{0}'.format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        self.country_selection = None
        self.selection_method = None
        self.drawn_feat = None

    def get_not_null_attrs(self):
        return dict((k, v) for k, v in self.__dict__.items() if v is not None)

    def display_on_map(self, map_, dc, asset_ee):
        """ Display the current feature on a map

        Args:

            map_ (SepalMap): Map to display the element
            dc: drawing controls
            asset_ee: GEE Object

        """

        # Search if there is a selected feature, otherwise use all the assetId


        bounds = self.get_bounds(asset_ee, cardinal=True)
        map_.update_map(asset_ee, bounds=bounds, remove_last=True)


    def get_bounds(self, ee_asset, cardinal=False):
        """ Returns the min(lon,lat) and max(lon, lat) from the given asset

        Args:
            ee_asset (ee.object): GEE asset (FeatureCollection, Geometry)
            cardinal (boolean) (optional)


        Returns:
            If cardinal True: returns cardinal points tl, bl, tr, br
            If cardinal False: returns bounding box
        """

        # 
        ee_bounds = ee.FeatureCollection(ee_asset).geometry().bounds().coordinates()
        coords = ee_bounds.get(0).getInfo()
        ll, ur = coords[0], coords[2]

        # Get the bounding box
        min_lon, min_lat, max_lon, max_lat = ll[0], ll[1], ur[0], ur[1]


        # Get (x, y) of the 4 cardinal points
        tl = (min_lon, max_lat)
        bl = (min_lon, min_lat)
        tr = (max_lon, max_lat)
        br = (max_lon, min_lat)

        if cardinal:
            return tl, bl, tr, br

        return min_lon, min_lat, max_lon, max_lat
    
class TileAoi(sw.Tile):
    """render and bind all the variable to create an autonomous aoi selector. It will create a asset in you gee account with the name 'aoi_[aoi_name]'. The assetId will be added to io.assetId."""
    
    #constants
    SELECTION_METHOD =('Country boundaries', 'Draw a shape', 'Upload file', 'Use GEE asset')
    
    def __init__(io, **kwargs):
        
        #create the output
        aoi_output = Alert().add_msg(ms.AOI_MESSAGE)
        
        #create the inputs widgets 
        aoi_file_input = v.Select(
            items=utils.get_shp_files(), 
            label='Select a file', 
            v_model=None,
            class_='d-none'
        )
        wb.bind(aoi_file_input, io, 'file_input', aoi_output)
    
        aoi_file_name = v.TextField(
            label='Select a filename', 
            v_model=io.file_name,
            class_='d-none'
        )
        wb.bind(aoi_file_name, io, 'file_name', aoi_output)
    
        aoi_country_selection = v.Select(
            items=[*utils.create_FIPS_dic()], 
            label='Country/Province', 
            v_model=None,
            class_='d-none'
        )
        wb.bind(aoi_country_selection, io, 'country_selection', aoi_output)
    
        aoi_asset_name = v.TextField(
            label='Select a GEE asset', 
            v_model=None,
            class_='d-none'
        )
        wb.bind(aoi_asset_name, io, 'assetId', aoi_output)
    
        widget_list = [
            aoi_file_input, 
            aoi_file_name, 
            aoi_country_selection, 
            aoi_asset_name
        ]
        
        #create the map 
        dc, m = mapping.init_map()
        wb.handle_draw(dc, io, 'drawn_feat', aoi_output)
    
        #bind the input to the selected method 
        aoi_select_method = v.Select(items=selection_method, label='AOI selection method', v_model=None)
        wb.bindAoiMethod(aoi_select_method, widget_list, io, m, dc, selection_method)
    

        #create the validation button 
        aoi_select_btn = ProcessBtn('Select these inputs')
        wb.bindAoiProcess(aoi_select_btn, io, m, dc, aoi_output, selection_method)
    
        #assemble everything on a tile 
        inputs = v.Layout(
            _metadata={'mount-id': 'data-input'},
            class_="pa-5",
            row=True,
            align_center=True, 
            children=[
                v.Flex(xs12=True, children=[aoi_select_method]),
                v.Flex(xs12=True, children=[aoi_country_selection]),
                v.Flex(xs12=True, children=[aoi_file_input]),
                v.Flex(xs12=True, children=[aoi_file_name]),
                v.Flex(xs12=True, children=[aoi_asset_name]),
                v.Flex(xs12=True, children=[aoi_select_btn]),
                v.Flex(xs12=True, children=[aoi_output]),
            ]
        )
        
        aoi_content_main = v.Layout(
            row=True,
            xs12=True,
            children = [
                v.Flex(xs12=True, md6=True, children=[inputs]),
                v.Flex(class_="pa-5", xs12=True, md6=True, children=[m])
            ]
        )
        
        super().__init__(
            id_='aoi_widget',
            title='AOI selection', 
            inputs=[aoi_content_main]
        )