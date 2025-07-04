"""GEEInterface class for Earth Engine operations."""

import asyncio
import threading
import traceback
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union

import ee
from eeclient.client import EESession
from eeclient.data import MapTileOptions
from eeclient.export.image import ImageFileFormat

from sepal_ui.logger import log
from sepal_ui.scripts import gee
from sepal_ui.scripts.gee_task import GEETask, R, TaskState


class GEEInterface:
    def __init__(self, session: Optional[EESession] = None):
        """A unified interface for Earth Engine operations.

        If a session is provided at initialization, custom EESession-based calls are used.
        Otherwise, the default Earth Engine API methods are invoked.
        """
        self.session = session
        self._closed = False

        self._async_loop = asyncio.new_event_loop()
        self._async_loop.set_debug(True)  # Enable debug mode for the event loop
        self._async_thread = threading.Thread(target=self._async_loop.run_forever, daemon=True)
        self._async_thread.start()

    def create_task(
        self,
        func: Callable[..., Coroutine[Any, Any, R]],
        key: Optional[str] = None,
        on_progress: Optional[Callable[[float, str], None]] = None,
        on_done: Optional[Callable[[R], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_finally: Optional[Callable[[], None]] = None,
    ) -> GEETask[R]:
        """Factory for GEETask bound to this interface's loop, with callbacks wired."""
        task = GEETask(loop=self._async_loop, function=func, key=key, on_finally=on_finally)

        if on_progress:
            task.observe(
                lambda change: on_progress(change["new"], task.message),
                names="progress",
            )
        if on_done:

            def _done(change):
                if change["new"] is TaskState.FINISHED:
                    on_done(task.result)

            task.observe(_done, names="state")
        if on_error:

            def _err(change):
                if change["new"] is TaskState.ERROR:
                    on_error(task.error)

            task.observe(_err, names="state")

        task.observe(
            lambda change: log.debug(f"Task {task.key} state changed to {change}"),
        )

        return task

    def _log_thread_info(self, operation: str) -> None:
        """Log information about current thread context for debugging."""
        current_thread = threading.current_thread()
        main_thread = threading.main_thread()
        log.debug(
            f"[{operation}] Current thread: {current_thread.name} (ID: {current_thread.ident})"
        )
        log.debug(f"[{operation}] Main thread: {main_thread.name} (ID: {main_thread.ident})")
        log.debug(
            f"[{operation}] GEE thread: {self._async_thread.name} (ID: {self._async_thread.ident})"
        )

    def _run_async_blocking(self, coro: asyncio.coroutine, timeout: Optional[float] = 305.0) -> Any:
        """Schedule `coro` in our private loop, block until done."""
        if self._closed:
            raise RuntimeError("GEEInterface is closed")

        operation = str(coro).split("(")[0].split(".")[-1] if "(" in str(coro) else str(coro)
        self._log_thread_info(f"STARTING {operation}")

        log.debug(f"Running sync coroutine: {coro}")

        try:
            future = asyncio.run_coroutine_threadsafe(coro, self._async_loop)
            result = future.result(timeout=timeout)
            log.debug(f"Sync coroutine completed successfully: {operation}")
            return result
        except asyncio.TimeoutError as e:
            log.error(f"Timeout ({timeout}s) running coroutine: {operation}")
            log.error(f"Traceback: {traceback.format_exc()}")
            # Cancel the future to clean up
            future.cancel()
            raise TimeoutError(f"Operation {operation} timed out after {timeout} seconds") from e
        except Exception as e:
            log.error(f"Error running sync coroutine {operation}: {type(e).__name__}: {e}")
            log.error(f"Full traceback: {traceback.format_exc()}")
            self._log_thread_info(f"ERROR in {operation}")
            # Re-raise the original exception to preserve the stack trace
            raise

    async def get_info_async(
        self, ee_object: ee.ComputedObject = None, tag: Any = None, serialized_object=None
    ) -> Dict:
        """Asynchronously get_info for an Earth Engine object."""
        try:
            if self.session:
                return await self.session.operations.get_info_async(
                    ee_object, tag, serialized_object=serialized_object
                )
            return await asyncio.to_thread(ee_object.getInfo)
        except Exception as e:
            log.error(f"Failed to get info for EE object: {type(e).__name__}: {e}")
            raise

    async def get_map_id_async(
        self,
        ee_image: ee.Image,
        vis_params: Optional[MapTileOptions] = None,
        bands: Optional[str] = None,
        format: Optional[str] = None,
    ) -> Dict:
        """Asynchronously get map ID for an Earth Engine image."""
        try:
            if self.session:
                return await self.session.operations.get_map_id_async(
                    ee_image, vis_params, bands, format
                )
            return await asyncio.to_thread(ee_image.getMapId, vis_params)
        except Exception as e:
            log.error(f"Failed to get map ID for EE image: {type(e).__name__}: {e}")
            raise

    async def get_asset_async(self, asset_id: str, not_exists_ok: bool = False) -> Dict:
        """Asynchronously get an asset by its ID."""
        try:
            if self.session:
                return await self.session.operations.get_asset_async(asset_id, not_exists_ok)

            if not_exists_ok:
                try:
                    return await asyncio.to_thread(ee.data.getAsset, asset_id)
                except Exception:
                    log.error(f"Asset not found: {asset_id}")
                    return None

            return await asyncio.to_thread(ee.data.getAsset, asset_id)
        except Exception as e:
            log.error(f"Failed to get asset {asset_id}: {type(e).__name__}: {e}")
            if not_exists_ok:
                return None
            raise

    async def get_assets_async(self, folder: str = "") -> List[Dict]:
        """Asynchronously get assets in a specified folder."""
        if self.session:
            return await self.session.operations.get_assets_async(folder)

        return await asyncio.to_thread(gee.get_assets, folder)

    async def get_folder_async(self) -> str:
        """Asynchronously get the assets folder path."""
        if self.session:
            return await self.session.get_assets_folder()
        return f"projects/{ee.data._cloud_api_user_project}/assets/"

    async def export_table_to_asset_async(
        self,
        collection: ee.FeatureCollection,
        asset_id: str,
        description: str = "myExportTableTask",
        selectors: Optional[list] = None,
        max_vertices: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> str:
        """Asynchronously export a FeatureCollection to an asset."""
        if self.session:
            return await self.session.export.table_to_asset_async(
                collection=collection,
                asset_id=asset_id,
                description=description,
                selectors=selectors,
                max_vertices=max_vertices,
                priority=priority,
            )
        else:
            task = ee.batch.Export.table.toAsset(
                collection=collection,
                assetId=asset_id,
                description=description,
                selectors=selectors,
                maxVertices=max_vertices,
                priority=priority,
            )
            task.start()
            return task

    async def is_running_async(self, name: str) -> bool:
        """Asynchronously check if a task is running by its name."""
        if self.session:
            task = await self.session.tasks.get_task_by_name_async(name)
            return bool(task and task["state"] in ("RUNNING", "READY"))
        return await asyncio.to_thread(gee.is_running, name)

    async def create_folder_async(self, folder_path: str) -> Dict:
        """Asynchronously create a folder in Earth Engine assets."""
        if self.session:
            return await self.session.operations.create_folder_async(folder_path)
        else:
            return await asyncio.to_thread(ee.data.createAsset, {"type": "FOLDER"}, folder_path)

    async def export_image_to_asset_async(
        self,
        image: ee.Image,
        asset_id: str,
        description: str = "myExportTableTask",
        max_pixels: Optional[int] = None,
        grid: Optional[dict] = None,
        request_id: Optional[str] = None,
        workload_tag: Optional[str] = None,
        priority: Optional[int] = None,
        region: Union[ee.Geometry, ee.Geometry.LinearRing, ee.Geometry.Polygon, str] = None,
        scale: Optional[float] = None,
        crs: Optional[str] = None,
        crs_transform: Optional[dict] = None,
        pyramid_policy: Optional[str] = None,
    ) -> str:
        """Asynchronously export an image to an asset."""
        if self.session:
            return await self.session.export.image_to_asset_async(
                image=image,
                asset_id=asset_id,
                description=description,
                max_pixels=max_pixels,
                grid=grid,
                request_id=request_id,
                workload_tag=workload_tag,
                priority=priority,
                region=region,
                scale=scale,
                crs=crs,
                crs_transform=crs_transform,
            )
        else:
            task = ee.batch.Export.image.toAsset(
                image=image,
                assetId=asset_id,
                description=description,
                maxPixels=max_pixels,
                grid=grid,
                requestId=request_id,
                workloadTag=workload_tag,
                priority=priority,
                region=region,
                scale=scale,
                crs=crs,
                crsTransform=crs_transform,
                pyramidPolicy=pyramid_policy,
            )
            task.start()
            return task

    async def export_image_to_drive_async(
        self,
        image: ee.Image,
        description: str = "myExportImageTask",
        folder: Optional[str] = None,
        filename_prefix: Optional[str] = None,
        dimensions: Optional[str] = None,
        region: Optional[ee.Geometry] = None,
        scale: Optional[float] = None,
        crs: Optional[str] = None,
        crs_transform: Optional[List[float]] = None,
        max_pixels: Optional[int] = None,
        skip_empty_tiles: Optional[bool] = None,
        file_format: Optional[str] = ImageFileFormat.GEO_TIFF,
        format_options: Optional[Dict] = None,
        priority: Optional[int] = None,
    ) -> str:
        """Asynchronously export an image to Google Drive."""
        if self.session:
            return await self.session.export.image_to_drive_async(
                image=image,
                filename_prefix=filename_prefix,
                folder=folder,
                file_format=file_format,
                description=description,
                max_pixels=max_pixels,
                region=region,
                scale=scale,
                crs=crs,
                crs_transform=crs_transform,
                priority=priority,
            )
        else:
            task = ee.batch.Export.image.toDrive(
                image=image,
                description=description,
                folder=folder,
                fileNamePrefix=filename_prefix,
                dimensions=dimensions,
                region=region,
                scale=scale,
                crs=crs,
                crsTransform=crs_transform,
                maxPixels=max_pixels,
                skipEmptyTiles=skip_empty_tiles,
                fileFormat=file_format,
                formatOptions=format_options,
                priority=priority,
            )
            task.start()
            return task

    def get_info(
        self,
        ee_object: ee.ComputedObject = None,
        tag: Any = None,
        timeout: Optional[float] = None,
        serialized_object=None,
    ) -> Dict:
        """Get info for an Earth Engine object, blocking until done."""
        return self._run_async_blocking(
            self.get_info_async(ee_object, tag, serialized_object=serialized_object), timeout
        )

    def get_map_id(
        self,
        ee_image: ee.Image,
        vis_params: Optional[MapTileOptions] = None,
        bands: Optional[str] = None,
        format: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Dict:
        """Get map ID for an Earth Engine image, blocking until done."""
        return self._run_async_blocking(
            self.get_map_id_async(ee_image, vis_params, bands, format), timeout
        )

    def get_asset(self, asset_id: str, not_exists_ok: bool = False) -> Dict:
        """Get an asset by its ID, blocking until done."""
        return self._run_async_blocking(self.get_asset_async(asset_id, not_exists_ok))

    def get_assets(self, folder: str = "") -> Dict:
        """Get assets in a specified folder, blocking until done."""
        return self._run_async_blocking(self.get_assets_async(folder))

    def get_folder(self) -> str:
        """Get the assets folder path, blocking until done."""
        return self._run_async_blocking(self.get_folder_async())

    def export_table_to_asset(
        self,
        collection: ee.FeatureCollection,
        asset_id: str,
        description: str = "myExportTableTask",
        selectors: Optional[list] = None,
        max_vertices: Optional[int] = None,
        priority: Optional[int] = None,
    ) -> str:
        """Export a FeatureCollection to an asset, blocking until done."""
        return self._run_async_blocking(
            self.export_table_to_asset_async(
                collection=collection,
                asset_id=asset_id,
                description=description,
                selectors=selectors,
                max_vertices=max_vertices,
                priority=priority,
            )
        )

    def is_running(self, asset_name: str) -> bool:
        """Check if a task is running by its name, blocking until done."""
        return self._run_async_blocking(self.is_running_async(asset_name))

    def create_folder(self, folder_path: str) -> Dict:
        """Create a folder in Earth Engine assets, blocking until done."""
        return self._run_async_blocking(self.create_folder_async(folder_path))

    def export_image_to_asset(
        self,
        image: ee.Image,
        asset_id: str,
        description: str = "myExportImageTask",
        region: Optional[ee.Geometry] = None,
        scale: Optional[float] = None,
        crs: Optional[str] = None,
        crs_transform: Optional[List[float]] = None,
        max_pixels: Optional[int] = None,
        pyramid_policy: Optional[str] = None,
        priority: Optional[int] = None,
    ) -> str:
        """Export an image to an asset, blocking until done."""
        return self._run_async_blocking(
            self.export_image_to_asset_async(
                image=image,
                asset_id=asset_id,
                description=description,
                region=region,
                scale=scale,
                crs=crs,
                crs_transform=crs_transform,
                max_pixels=max_pixels,
                pyramid_policy=pyramid_policy,
                priority=priority,
            )
        )

    def export_image_to_drive(
        self,
        image: ee.Image,
        description: str = "myExportImageTask",
        folder: Optional[str] = None,
        filename_prefix: Optional[str] = None,
        dimensions: Optional[str] = None,
        region: Optional[ee.Geometry] = None,
        scale: Optional[float] = None,
        crs: Optional[str] = None,
        crs_transform: Optional[List[float]] = None,
        max_pixels: Optional[int] = None,
        skip_empty_tiles: Optional[bool] = None,
        file_format: Optional[str] = ImageFileFormat.GEO_TIFF,
        format_options: Optional[Dict] = None,
        priority: Optional[int] = None,
    ) -> str:
        """Export an image to Google Drive, blocking until done."""
        return self._run_async_blocking(
            self.export_image_to_drive_async(
                image=image,
                description=description,
                folder=folder,
                filename_prefix=filename_prefix,
                dimensions=dimensions,
                region=region,
                scale=scale,
                crs=crs,
                crs_transform=crs_transform,
                max_pixels=max_pixels,
                skip_empty_tiles=skip_empty_tiles,
                file_format=file_format,
                format_options=format_options,
                priority=priority,
            )
        )

    def close(self) -> None:
        """Close the GEEInterface and clean up resources."""
        if self._closed:
            return

        self._closed = True
        log.debug("Closing GEEInterface...")

        try:
            if hasattr(self, "_sync_loop") and self._async_loop.is_running():
                self._async_loop.call_soon_threadsafe(self._async_loop.stop)
                if hasattr(self, "_sync_thread") and self._async_thread.is_alive():
                    self._async_thread.join(timeout=5.0)
                    if self._async_thread.is_alive():
                        log.warning("Background thread did not stop within timeout")
                if not self._async_loop.is_closed():
                    self._async_loop.close()

            log.debug("GEEInterface closed successfully")
        except Exception as e:
            log.error(f"Error during GEEInterface cleanup: {e}")

    def __enter__(self):
        """Support for context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support for context manager protocol - automatically close resources."""
        self.close()

    def __del__(self):
        """Destructor to ensure resources are cleaned up."""
        try:
            if not self._closed:
                self.close()
        except Exception:
            # Ignore errors during cleanup in destructor
            pass
