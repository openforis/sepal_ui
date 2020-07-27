import time
import sys
import re
import os

import ee
import geemap

from sepal_ui.scripts import utils, gee
from sepal_ui.scripts import messages as ms

#initialize earth engine
ee.Initialize()

def isAsset(asset_descripsion, folder):
    """Check if the asset already exist in the user asset folder
    
    Args: 
        asset_descripsion (str) : the descripsion of the asset
        folder (str): the folder of the glad assets
        
    Returns:
        exist (bool): true if already in folder
    """
    exist = False
    liste = ee.data.listAssets({'parent': folder})['assets']
    for asset in liste:
        if asset['name'] == folder + asset_descripsion:
            exist = True
            break
    return exist    

def run_aoi_selection(file_input, file_name, country_selection, asset_name, drawing_method, widget_alert, list_method, drawn_feat):
    """ create an gee asset according to the user inputs

    Args:
        file_input (str): the file to retreive from the user folder. It must be a .shp file
        file_name (str): name of the aoi that will be used troughout the process
        country_selection (str): a country name in english available in LSIB 2017
        asset_name (str): the assetId of a existing asset
        drawing_method (str): the name of the method selected to create the asset
        widget_alert (v.Alert): the widget used to display the process informations
        list_method ([str]): list of the method use to select an AOI
        drawn_feat (ee.FeatureCollection): the last drawn object on the map
        
    Returns:
        asset (str) : the AssetId of the AOI
    """
    #go to the glad folder in gee assets 
    folder = ee.data.getAssetRoots()[0]['id'] + '/'
    
    #check the drawing method
    if drawing_method == None: #not selected
        utils.displayIO(widget_alert, ms.NO_SELECTION, 'warning')    
        asset = None
        
    elif drawing_method == list_method[0]: #use a country boundary
        if country_selection == None:
            utils.displayIO(widget_alert, ms.NO_COUNTRY, 'warning') 
            asset = None
            return asset
        country_code = utils.create_FIPS_dic()[country_selection] 
        asset_descripsion = ms.FILE_PATTERN.format(country_code) 
        asset = folder + asset_descripsion
            
        #check asset existence
        if isAsset(asset_descripsion, folder):
            utils.displayIO(widget_alert, ms.ASSET_ALREADY_EXIST.format(asset), 'success')
            return asset
        
        country = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017').filter(ee.Filter.eq('country_co', country_code))
                
        #create and launch the task
        task_config = {
            'collection': country, 
            'description':asset_descripsion,
            'assetId': asset
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()
        gee.wait_for_completion(asset_descripsion, widget_alert)
          
        utils.displayIO(widget_alert, ms.ASSET_CREATED.format(asset), 'success')
                
    elif drawing_method == list_method[1]: #draw a shape
             
        aoi = drawn_feat 
        asset_name = ms.FILE_PATTERN.format(re.sub('[^a-zA-Z\d\-\_]', '_', file_name))
        
        #check if something is drawn 
        if drawn_feat == None:
            asset = None
            utils.displayIO(widget_alert, ms.NO_SHAPE, 'error')
            return asset
              
        #check asset existence
        if isAsset(asset_name, folder):
            asset = None
            utils.displayIO(widget_alert, ms.NAME_USED, 'error')
            return asset 
        
        asset = folder + asset_name
            
        #create and launch the task
        task_config = {
            'collection': aoi, 
            'description':asset_name,
            'assetId': asset
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()
        gee.wait_for_completion(asset_name, widget_alert)
           
        utils.displayIO(widget_alert, ms.ASSET_CREATED.format(asset), 'success')           
            
    elif drawing_method == list_method[3]: #use GEE asset
        
        #verify that there is an asset
        if asset_name == '' or asset_name == None:
            asset = None
            utils.displayIO(widget_alert, ms.NO_ASSET, 'error') 
        else:
            asset = asset_name
            utils.displayIO(widget_alert, ms.CHECK_IF_ASSET, 'info')
            
    elif drawing_method == list_method[2]: #upload file
        home_path = os.path.expanduser('~')
        file_input = home_path + '/' + file_input
        print(file_input)
        try:
            ee_object = geemap.shp_to_ee(file_input)
        except:
            utils.displayIO(widget_alert, ms.ERROR_OCCURED, 'error')
            asset = None
            return asset
        
        name = os.path.split(file_input)[1]
        
        asset_name = ms.FILE_PATTERN.format(re.sub('[^a-zA-Z\d\-\_]','_',name))
        
        #check asset's name
        if isAsset(asset_name, folder):
            asset = None
            utils.displayIO(widget_alert, ms.NAME_USED, 'error')
        else:
            asset = folder + asset_name
            
            #launch the task
            task_config = {
                'collection': ee_object, 
                'description':asset_name,
                'assetId': asset
            }
            task = ee.batch.Export.table.toAsset(**task_config)
            task.start()
            gee.wait_for_completion(asset_name, widget_alert)
                   
            utils.displayIO(widget_alert, ms.ASSET_CREATED.format(asset), 'success')
            
    return asset