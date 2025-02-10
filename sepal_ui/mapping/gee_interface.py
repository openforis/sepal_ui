"""GEEInterface class for Earth Engine operations."""

from typing import Optional

import ee

# Import your custom session object and EE exception.
from eeclient.client import EESession
from eeclient.data import MapTileOptions

# Type aliases for clarity.
Image = ee.image.Image
ImageCollection = ee.imagecollection.ImageCollection
Feature = ee.feature.Feature
FeatureCollection = ee.featurecollection.FeatureCollection
ComputedObject = ee.computedobject.ComputedObject


class GEEInterface:
    def __init__(self, session: Optional[EESession] = None):
        """A unified interface for Earth Engine operations.

        If a session is provided at initialization, custom session-based calls are used.
        Otherwise, the default Earth Engine API methods are invoked.
        """
        self.session = session

    def get_info(self, ee_object: ee.ComputedObject, workloadTag=None):
        """Get the info of an Earth Engine object.

        Uses the custom session if available; otherwise falls back to ee_object.getInfo().

        Args:
            ee_object: The Earth Engine computed object.
            workloadTag: (Optional) A workload tag.

        Returns:
            The result from the Earth Engine API.
        """
        if self.session:
            return self.session.operations.get_info(ee_object, workloadTag)
        else:
            return ee_object.getInfo()

    def get_map_id(
        self,
        ee_image: ee.Image,
        vis_params: Optional[MapTileOptions] = None,
        bands: Optional[str] = None,
        format: Optional[str] = None,
    ):
        """Get the map id of an image.

        Uses the custom session if available; otherwise falls back to ee_image.getMapId().

        Args:
            ee_image: The Earth Engine image.
            vis_params: (Optional) Visualization parameters.
            bands: (Optional) The bands to display.
            format: (Optional) The image file format.

        Returns:
            A dictionary containing map id, token, and a TileFetcher.
        """
        if self.session:
            return self.session.operations.get_map_id(ee_image, vis_params, bands, format)
        else:
            return ee_image.getMapId(vis_params)
