"""GEEInterface class for Earth Engine operations."""

import asyncio
from typing import Optional

import ee
from eeclient.client import EESession
from eeclient.data import MapTileOptions

from sepal_ui.logger.logger import logger
from sepal_ui.scripts import gee


class GEEInterface:
    def __init__(self, session: Optional[EESession] = None):
        """A unified interface for Earth Engine operations.

        If a session is provided at initialization, custom session-based calls are used.
        Otherwise, the default Earth Engine API methods are invoked.
        """
        logger.debug("Initializing GEEInterface.")
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
            logger.debug("Using custom session to get info.")
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

    def get_asset(self, asset_id: str, not_exists_ok: bool = False):
        """Get an asset by its ID.

        Uses the custom session if available; otherwise falls back to ee.data.getAsset().

        Args:
            asset_id: The asset ID.

        Returns:
            The asset object.
        """
        logger.debug(f"Getting asset with ID: {asset_id}")
        if self.session:
            return self.session.operations.get_asset(asset_id, not_exists_ok=False)
        else:
            if not_exists_ok:
                try:
                    return ee.data.getAsset(asset_id)
                except Exception:
                    logger.error(f"Asset not found: {asset_id}")
                    return None
            return ee.data.getAsset(asset_id)

    def get_assets(self, folder: str = ""):
        """Get all the assets from the parameter folder.

        Uses the custom session if available; otherwise falls back to ee.data.listAssets().

        Args:
            folder: The initial GEE folder.

        Returns:
            The asset list. Each asset is a dict with 3 keys: 'type', 'name', and 'id'.
        """
        if isinstance(self.session, EESession):
            assets = asyncio.run(self.session.operations.get_assets_async(folder))
            logger.debug(f"Got assets: {assets}")
            return assets
        else:
            # That function will use ee.data.listAssets() to get the assets.
            # if it fails, it will use the synchronous version of the function.
            return gee.get_assets(folder)

    def get_folder(self):
        """Get all the assets from the parameter folder.

        Uses the custom session if available; otherwise falls back to ee.data.listAssets().

        Args:
            folder: The initial GEE folder.

        Returns:
            The asset list. Each asset is a dict with 3 keys: 'type', 'name', and 'id'.
        """
        if isinstance(self.session, EESession):
            return self.session.get_assets_folder()
        else:
            return f"projects/{ee.data._cloud_api_user_project}/assets/"

    def export_table_to_asset(
        self,
        collection: ee.FeatureCollection,
        asset_id: str,
        description: str = "myExportTableTask",
        selectors: Optional[list] = None,
        max_vertices: Optional[int] = None,
        priority: Optional[int] = None,
    ):
        """Export a table to an asset.

        Uses the custom session if available; otherwise falls back to ee.data.exportTable().

        Args:
            asset_name: The name of the asset to export to.
            description: (Optional) The description of the export task.
            selectors: (Optional) The selectors to export.
            max_vertices: (Optional) The maximum number of vertices.
            priority: (Optional) The priority of the task.

        Returns:
            The task ID.
        """
        if self.session:
            return self.session.export.table_to_asset(
                collection, asset_id, description, selectors, max_vertices, priority
            )
        else:
            return ee.batch.Export.table.toAsset(
                collection=collection,
                assetId=asset_id,
                description=description,
                selectors=selectors,
                maxVertices=max_vertices,
                priority=priority,
            ).start()

    def is_running(self, asset_name: str):
        """Check if a task is running.

        Uses the custom session if available; otherwise falls back to ee.data.getTaskStatus().

        Args:
            asset_name: The asset name.

        Returns:
            True if the task is running.
        """
        if self.session:
            task = self.session.tasks.get_task_by_name(asset_name)
            if task:
                return task["state"] in ["RUNNING", "READY"]
            return False
        else:
            return gee.is_running(asset_name)
