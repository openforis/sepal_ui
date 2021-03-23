import time
import sys
import re
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
    """
    remove the manifest from the asset name and display it to the user in an output
    
    Args: 
        output (sw.Alert): the alert to display information to the user
        asset (str): the asset name
    
    Return:
        (str): the asset name without the manifest
    """
    
    asset = asset.replace('projects/earthengine-legacy/assets/', '')
    
    output.add_msg(ms.aoi_sel.asset_created.format(asset), 'success')
    
    return asset

def isAsset(asset_descripsion, folder):
    """
    Check if the asset already exist in the user asset folder
    
    Args: 
        asset_descripsion (str) : the descripsion of the asset
        folder (str): the folder of the glad assets
        
    Return:
        (bool): true if already in folder
    """
    exist = False
    liste = ee.data.listAssets({'parent': folder})['assets']
    for asset in liste:
        if asset['name'] == str(Path(folder,asset_descripsion)):
            exist = True
            break
            
    return exist 

def get_admin0_asset(adm0, output):
    """
    send a request to GEE to get a featurecollection based on the country selected
    
    Args:
        adm0 (int): the administrative level 0 in FAO GAUL 2015
        output (sw.Alert): the alert to display information to the end user
        
    return:
        (ee.FeatureColection): the FeatureCollection invocation of the country
    """
    
    if adm0 == None:
        output.add_msg(ms.aoi_sel.no_country, 'warning')
        return (None, None)
    
    country = ee.FeatureCollection("FAO/GAUL/2015/level0").filter(ee.Filter.eq('ADM0_CODE', adm0))
    
    #output.add_msg(ms.aoi_sel.valid_admin0.format(iso_3), 'success')
    
    return country

def get_admin1_asset(adm1, output):
    """
    send a request to GEE to get a featurecollection based on the country selected
    
    Args:
        adm1 (int): the administrative level 1 in FAO GAUL 2015
        output (sw.Alert): the alert to display information to the end user
        
    return:
        (ee.FeatureColection): the FeatureCollection invocation of the country
    """
    
    if adm1 == None:
        output.add_msg(ms.aoi_sel.no_country, 'warning')
        return (None, None)
    
    country = ee.FeatureCollection("FAO/GAUL/2015/level1").filter(ee.Filter.eq('ADM1_CODE', adm1))
    
    #
    
    return country

def get_admin2_asset(adm2, output):
    """
    send a request to GEE to get a featurecollection based on the country selected
    
    Args:
        adm2 (int): the administrative level 2 in FAO GAUL 2015
        output (sw.Alert): the alert to display information to the end user
        
    return:
        (ee.FeatureColection): the FeatureCollection invocation of the country
    """
    
    if adm2 == None:
        output.add_msg(ms.aoi_sel.no_country, 'warning')
        return (None, None)
    
    country = ee.FeatureCollection("FAO/GAUL/2015/level2").filter(ee.Filter.eq('ADM2_CODE', adm2))
    
    #output.add_msg(ms.aoi_sel.valid_admin0.format(iso_3), 'success')
    
    return country

def get_drawn_shape(drawn_feat, file_name, folder, output):
    """
    send the requested drawn feature to GEE to create an asset
    
    Args:
        drawn_feat (ee.FeatureCollection): the feature drawn on the map
        file_name (str): the name to use as GEE asset
        folder (str): the path to the user GEE folder
        output (sw.Alert): the alert to display information to the end user
        
    Return:
        (str): the created asset name
    """
    
    aoi = drawn_feat 
    asset_name = ms.aoi_sel.file_pattern.format(re.sub('[^a-zA-Z\d\-\_]', '_', file_name))
        
    if drawn_feat == None: #check if something is drawn 
        output.add_msg(ms.aoi_sel.no_shape, 'error')
        return None
    elif isAsset(asset_name, folder): #check asset existence
        output.add_msg(ms.aoi_sel.name_used, 'error')
        return None 
        
    asset = str(Path(folder, asset_name))
            
    # create and launch the task
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
    """
    check that the asset name is not null or None
    
    Args:
        asset_name (str): the asset name
        output (sw.Alert): the alert to display information to the end user
        
    Return:
        (str): return the asset if not null
    """
    
    if asset_name == '' or asset_name == None:
        output.add_msg(ms.aoi_sel.no_asset, 'error') 
        asset = None
    else:
        output.add_msg(ms.aoi_sel.check_if_asset, 'success')
        asset = asset_name
        
    return asset

def get_csv_asset(json_csv, file_name, folder, output):
    """
    Send a request to GEE to create an asset based on the local shapefile
    
    Args:
        json_csv (str): the csv file information stored as a json dict {pathname, id, lng, lat}
        file_name (str): the name that will be used in GEE 
        folder (str): The user folder in GEE
        outpput (sw.Alert): the alert to display information to the end user
        
    Return:
        (str): the created asset name
    """
    
    # read the json 
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
    asset = str(Path(folder, asset_name))
            
    # create and launch the task
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
    """
    Send a request to GEE to create an asset based on the local shapefile
    
    Args:
        file_input (str | pathlib.path): the path to the .shp file
        file_name (str): the name used for the GEE asset
        folder (str): the user folder in GEE
        output (sw.Alert): the alert to display information to the end user
        
    Return:
        (str): the created asset name
    """
    
    if type(file_input) == str:
        file_input = Path(file_input)
        
    if not file_input.is_file():
        output.add_msg(ms.aoi_sel.error_occured, 'error')
        return None
    
    # convert the .shp in gdf in epsg:4326
    gdf = gpd.read_file(file_input).to_crs('EPSG:4326')
    
    # convert gdf to geo json 
    json_gdf = json.loads(gdf.to_json())
    
    # create ee_object based on the json dict
    ee_object = geemap.geojson_to_ee(json_gdf)           
       
    asset_name = ms.aoi_sel.file_pattern.format(re.sub('[^a-zA-Z\d\-\_]','_',file_name))
        
    # check asset's name
    if isAsset(asset_name, folder):
        output.add_msg(ms.aoi_sel.name_used, 'error')
        asset = None
        
    else:
        
        asset = str(Path(folder, asset_name))
            
        # launch the task
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
    """
    Create an gee asset according to the user inputs

    Args:
        io.file_input (str): the file to retreive from the user folder. It must be a .shp file
        io.file_name (str): name of the aoi that will be used troughout the process
        io.country_selection (str): a country name in english available in LSIB 2017
        io.asset_name (str): the assetId of a existing asset
        io.drawing_method (str): the name of the method selected to create the asset
        output (v.Alert): the widget used to display the process informations
        list_method ([str]): list of the method use to select an AOI
        drawn_feat (ee.FeatureCollection): the last drawn object on the map
        folder (str, optional): the user GEE asset folder
        
    Return:
        (str) : the AssetId of the AOI
    """
    # go to the glad folder in gee assets 
    if not folder: 
        folder = ee.data.getAssetRoots()[0]['id']
    
    # clean all but the selected method
    if io.adm0:
        io.assetId = None
    else:
        io.feature_collection, io.country_code = (None, None)
    
    
    # check the aoi method used
    
    # not selected
    if io.selection_method == None:
        raise Exception(ms.aoi_sel.no_selection)   
    # use a country boundary
    elif io.selection_method == list_method[0]: 
        asset = get_admin0_asset(io.adm0, output)
        io.set_admin(asset, admin0=io.adm0)
        output.add_msg(ms.aoi_sel.valid_admin0.format(io.get_aoi_name()), 'success')
    # use adm1
    elif io.selection_method == list_method[1]: 
        asset = get_admin1_asset(io.adm1, output)
        io.set_admin(asset, admin0=io.adm0, admin1=io.adm1)
        output.add_msg(ms.aoi_sel.valid_admin0.format(io.get_aoi_name()), 'success')
    # use adm2
    elif io.selection_method == list_method[2]: 
        asset = get_admin2_asset(io.adm2, output)
        io.set_admin(asset, admin0=io.adm0, admin1=io.adm1, admin2=io.adm2)
        output.add_msg(ms.aoi_sel.valid_admin0.format(io.get_aoi_name()), 'success')
    # draw a shape
    elif io.selection_method == list_method[3]: 
        io.set_asset(get_drawn_shape(io.drawn_feat, io.file_name, folder, output))
    # use GEE asset
    elif io.selection_method == list_method[4]: 
        io.set_asset(get_gee_asset(io.assetId, output))
    # upload file
    elif io.selection_method == list_method[5]: 
        io.set_asset(get_shp_aoi(io.file_input, io.file_name, folder, output))
    # csv point file
    elif io.selection_method == list_method[6]: 
        io.set_asset(get_csv_asset(io.json_csv, io.file_name, folder, output))
            
    return