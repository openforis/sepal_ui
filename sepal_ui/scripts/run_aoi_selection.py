import time
import sys
import re
import os
import json
from pathlib import Path

import ee
import geemap
import pandas as pd
import geopandas as gpd

from sepal_ui.scripts import utils, gee
from sepal_ui.message import ms
from sepal_ui.scripts import utils as su
    
# initialize earth engine
su.init_ee()

def display_asset(output, asset):
    """remove the manifest from the asset name and display it to the user"""
    
    asset = asset.replace('projects/earthengine-legacy/assets/', '')
    
    output.add_msg(ms.aoi_sel.asset_created.format(asset), 'success')
    
    return

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
        if asset['name'] == os.path.join(folder,asset_descripsion):
            exist = True
            break
            
    return exist 

def get_country_asset(country_selection, output):
    """send a request to GEE to get a featurecollection based on the country selected"""
    
    if country_selection == None:
        output.add_msg(ms.aoi_sel.no_country, 'warning')
        return (None, None)
    
    country_code = utils.get_gaul_dic()[country_selection] 
    iso_3 = utils.get_iso_3(country_selection)
    
    country = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq('ADM0_CODE', country_code))
          
    display_asset(output, iso_3)
    
    return country, iso_3

def get_drawn_shape(drawn_feat, file_name, folder, output):
    """send the requested drawn feature to GEE to create an asset"""
    
    aoi = drawn_feat 
    asset_name = ms.aoi_sel.file_pattern.format(re.sub('[^a-zA-Z\d\-\_]', '_', file_name))
        
    if drawn_feat == None: #check if something is drawn 
        output.add_msg(ms.aoi_sel.no_shape, 'error')
        return None
    elif isAsset(asset_name, folder): #check asset existence
        output.add_msg(ms.aoi_sel.name_used, 'error')
        return None 
        
    asset = os.path.join(folder, asset_name)
            
    #create and launch the task
    task_config = {
        'collection': drawn_feat, 
        'description':asset_name,
        'assetId': asset
    }
    task = ee.batch.Export.table.toAsset(**task_config)
    task.start()
    gee.wait_for_completion(asset_name, output)
           
    display_asset(output, asset)
    
    return asset

def get_gee_asset(asset_name, output):
    """check that the asset exist return None if not"""
    
    if asset_name == '' or asset_name == None:
        output.add_msg(ms.aoi_sel.no_asset, 'error') 
        asset = None
    else:
        output.add_msg(ms.aoi_sel.check_if_asset, 'success')
        asset = asset_name
        
    return asset

def get_csv_asset(json_csv, file_name, folder, output):
    """Send a request to GEE to create an asset based on the local shapefile"""
    
    #read the json 
    load_df = json.loads(json_csv)
    
    # check that the columns are well set 
    tmp_list = [load_df[i] for i in load_df]
    if not len(tmp_list) == len(set(tmp_list)):
        output.add_msg(ms.aoi_sel.duplicate_key, 'error') 
        return None
    
    # check asset existence
    asset_name = ms.aoi_sel.file_pattern.format(re.sub('[^a-zA-Z\d\-\_]', '_', file_name))
    if isAsset(asset_name, folder):
        output.add_msg(ms.aoi_sel.name_used, 'error')
        return None
    
    # create a tmp gdf
    df = pd.read_csv(load_df['pathname'], sep=None, engine='python')
    gdf = gpd.GeoDataFrame(df, crs='EPSG:4326', geometry = gpd.points_from_xy(df[load_df['lng_column']], df[load_df['lat_column']]))
    
    # convert it into geo-json 
    json_df = json.loads(gdf.to_json())
    
    # create a gee object with geemap
    output.add_msg(ms.aoi_sel.geojson_to_ee, 'success')
    ee_object = geemap.geojson_to_ee(json_df)
    
    # upload this object to earthengine
    asset = os.path.join(folder, asset_name)
            
    #create and launch the task
    task_config = {
        'collection': ee_object, 
        'description':asset_name,
        'assetId': asset
    }
    task = ee.batch.Export.table.toAsset(**task_config)
    task.start()
    gee.wait_for_completion(asset_name, output)
           
    display_asset(output, asset)
    
    return asset
    
            
def get_shp_aoi(file_input, file_name, folder, output):
    """send a request to GEE to create an asset based on the local shapefile"""
    
    if not os.path.isfile(file_input):
        output.add_msg(ms.aoi_sel.error_occured, 'error')
        return None
    
    # convert the .shp in gdf in epsg:4326
    gdf = gpd.read_file(file_input).to_crs('EPSG:4326')
    
    # convert gdf to geo json 
    json_gdf = json.loads(gdf.to_json())
    
    # create ee_object based on the json dict
    ee_object = geemap.geojson_to_ee(json_gdf)           
       
    asset_name = ms.aoi_sel.file_pattern.format(re.sub('[^a-zA-Z\d\-\_]','_',file_name))
        
    #check asset's name
    if isAsset(asset_name, folder):
        output.add_msg(ms.aoi_sel.name_used, 'error')
        asset = None
        
    else:
        
        asset = os.path.join(folder, asset_name)
            
        #launch the task
        task_config = {
            'collection': ee_object, 
            'description':asset_name,
            'assetId': asset
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()
        gee.wait_for_completion(asset_name, output)
                   
        display_asset(output, asset)
    
    return asset
    
def run_aoi_selection(output, list_method, io, folder=None):
    """ create an gee asset according to the user inputs

    Args:
        file_input (str): the file to retreive from the user folder. It must be a .shp file
        file_name (str): name of the aoi that will be used troughout the process
        country_selection (str): a country name in english available in LSIB 2017
        asset_name (str): the assetId of a existing asset
        drawing_method (str): the name of the method selected to create the asset
        output (v.Alert): the widget used to display the process informations
        list_method ([str]): list of the method use to select an AOI
        drawn_feat (ee.FeatureCollection): the last drawn object on the map
        
    Returns:
        asset (str) : the AssetId of the AOI
    """
    #go to the glad folder in gee assets 
    if not folder: 
        folder = ee.data.getAssetRoots()[0]['id']
    
    #clean all but the selected method
    if io.country_selection:
        io.assetId = None
    else:
        io.feature_collection, io.country_code = (None, None)
    
    
    # check the aoi method used
    
    # not selected
    if io.selection_method == None:
        output.add_msg(ms.aoi_sel.no_selection, 'error')   
    # use a country boundary
    elif io.selection_method == list_method[0]: 
        io.feature_collection, io.country_code = get_country_asset(io.country_selection, output)
    # draw a shape
    elif io.selection_method == list_method[1]: 
        io.assetId = get_drawn_shape(io.drawn_feat, io.file_name, folder, output)
    # use GEE asset
    elif io.selection_method == list_method[3]: 
        io.assetId = get_gee_asset(io.assetId, output)
    # upload file
    elif io.selection_method == list_method[2]: 
        io.assetId = get_shp_aoi(io.file_input, io.file_name, folder, output)
    # csv point file
    elif io.selection_method == list_method[4]: 
        io.assetId = get_csv_asset(io.json_csv, io.file_name, folder, output)
            
    return