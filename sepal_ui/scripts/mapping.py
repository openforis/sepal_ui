import geemap
import ee 
import shapely.geometry as sg
from haversine import haversine

#initialize earth engine
if not ee.data._credentials: ee.Initialize()

def init_map():
    '''Initialize a map centered on the point [0,0] with zoom at 1
    
    Returns:
        dc (DrawControl): a draw control for polygon drawing 
        m (Map): a map
    '''
    center = [0, 0]
    zoom = 2

    dc = geemap.DrawControl(
        marker={},
        circlemarker={},
        polyline={},
        rectangle={'shapeOptions': {'color': '#0000FF'}},
        circle={'shapeOptions': {'color': '#0000FF'}},
        polygon={'shapeOptions': {'color': '#0000FF'}},
     )

    m = geemap.Map(center=center, zoom=zoom)
    m.clear_layers()
    m.clear_controls()
    m.add_basemap('Esri Satellite')
    m.add_basemap('CartoDB.Positron')
    m.add_control(geemap.ZoomControl(position='topright'))
    m.add_control(geemap.LayersControl(position='topright'))
    m.add_control(geemap.AttributionControl(position='bottomleft'))
    m.add_control(geemap.ScaleControl(position='bottomleft', imperial=False))
    
    return (dc, m)

def update_map(m, dc, assetId):
    """Update the map with the asset overlay and by removing the selected drawing controls
    
    Args:
        m (Map): a map
        dc (DrawControl): the drawcontrol to be removed
        assetId (str): the asset ID in gee assets
    """  
    m.centerObject(ee.FeatureCollection(assetId), zoom=update_zoom(assetId))
    m.addLayer(ee.FeatureCollection(assetId), {'color': 'green'}, name='aoi')
    dc.clear()
    try:
        m.remove_control(dc)
    except:
        pass
    
def update_zoom(assetId):
    """search for the dimension of the AOI and adapt the map zoom acordingly
    
    Args: 
        assetId (str): the assetID
    
    Returns: 
        zoom (int): the zoom value riquired
    """
    
    #retreive the asset and transform it to shapely
    geom = ee.FeatureCollection(assetId).geometry()
    geomJson = geemap.ee_to_geojson(geom)
    geomShp = sg.shape(geomJson)
    
    #get the bounding box
    bb = {}
    bb['minx'], bb['miny'], bb['maxx'], bb['maxy'] = geomShp.bounds
    
    #create the 4 cardinal points
    tl = [bb['minx'], bb['maxy']]
    bl = [bb['minx'], bb['miny']]
    tr = [bb['maxx'], bb['maxy']]
    br = [bb['maxx'], bb['miny']]

    maxsize = max(haversine(tl, br), haversine(bl, tr))
    
    lg = 40075 #number of displayed km at zoom 1
    zoom = 1
    while lg > maxsize:
        zoom += 1
        lg /= 2
        
    return zoom-1