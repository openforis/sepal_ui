####################################
##      init ee with service      ##
####################################
import ee
import os 
import base64

if 'EE_PRIVATE_KEY' in os.environ:
    # key need to be decoded in a file
    content = base64.b64decode(os.environ['EE_PRIVATE_KEY']).decode()
    with open('ee_private_key.json', 'w') as f:
        f.write(content)
    
    # connection to the service account
    service_account = 'test-sepal-ui@sepal-ui.iam.gserviceaccount.com'
    credentials = ee.ServiceAccountCredentials(service_account, 'ee_private_key.json')
    ee.Initialize(credentials)

else:
    ee.Initialize()
####################################

import unittest

import ipyvuetify as v

from sepal_ui import aoi

class TestAoiTile(unittest.TestCase):

    def test_init(self):
        
        aoi_io = aoi.Aoi_io()
        
        #default init
        tile = aoi.TileAoi(aoi_io)
        
        self.assertIsInstance(tile, aoi.TileAoi)        
        
        return
        
if __name__ == '__main__':
    unittest.main()