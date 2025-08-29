"""Google Drive interface for SEPAL integration.

This module provides a GDriveInterface class that integrates with SEPAL credentials
to perform Google Drive operations such as file listing, downloading, and deletion.
"""

import io
import logging
from pathlib import Path
from typing import Optional

from apiclient import discovery
from eeclient.sepal_credential_mixin import SepalCredentialMixin
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload

logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)
log = logging.getLogger("sepalui.scripts.drive_interface")


class GDriveInterface(SepalCredentialMixin):
    """Google Drive interface with SEPAL credential integration.

    This class provides methods to interact with Google Drive using SEPAL credentials
    or file-based credentials. It supports automatic token refresh and various file operations.
    """

    def __init__(self, sepal_headers: Optional[dict] = None):
        """Initialize the Google Drive interface.

        Args:
            sepal_headers: Optional SEPAL headers dictionary for authentication.
                          If not provided, falls back to file-based credentials.

        Raises:
            ValueError: If credentials file not found or no access token available.
        """
        super().__init__(sepal_headers)

        self._service = None
        self.logger = logging.getLogger(f"eeclient.gdrive.{self.user}")

    def refresh_credentials(self) -> None:
        """Refresh credentials synchronously by calling SEPAL API or re-reading file."""
        self.set_credentials_sync()
        self._service = None

    @property
    def service(self):
        """Lazy property that ensures valid credentials and service."""
        if self.needs_credentials_refresh():
            self.refresh_credentials()

        if self._service is None:
            self._service = discovery.build(
                serviceName="drive",
                version="v3",
                cache_discovery=False,
                credentials=Credentials(self.access_token),
            )

        return self._service

    def print_file_list(self):
        """Print a list of files from Google Drive to the console."""
        service = self.service

        results = (
            service.files().list(pageSize=30, fields="nextPageToken, files(id, name)").execute()
        )
        items = results.get("files", [])
        if not items:
            log.info("No files found.")
        else:
            log.info("Files:")
            for item in items:
                log.info("{0} ({1})".format(item["name"], item["id"]))

    def get_items(self):
        """Get a list of CSV files from Google Drive.

        Returns:
            list: List of CSV files with their metadata.
        """
        service = self.service

        # get list of files
        results = (
            service.files()
            .list(
                q="mimeType='text/csv'",
                pageSize=1000,
                fields="nextPageToken, files(id, name)",
            )
            .execute()
        )
        items = results.get("files", [])

        return items

    def get_id(self, filename):
        """Get the Google Drive file ID for a given filename.

        Args:
            filename (str): Name of the file to search for.

        Returns:
            tuple: (success_flag, file_id_or_error_message)
        """
        items = self.get_items()

        # Find the file by name
        for item in items:
            if item["name"] == filename:
                return (1, item["id"])

        return (0, filename + " not found")

    def download_file(self, filename, output_file, sepal_client=None):
        """Download a file from Google Drive.

        Args:
            filename (str): Name of the file to download.
            output_file (str or Path): Path where the file should be saved.
            sepal_client: Optional SEPAL client for remote file operations.
        """
        # get file id
        success, fId = self.get_id(filename)
        if success == 0:
            log.error(f"File not found: {fId}")
            return

        request = self.service.files().get_media(fileId=fId)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        if sepal_client:
            sepal_client.set_file(output_file, fh.getvalue())
            return

        # Otherwise, write to local file
        file_obj = open(output_file, "wb")
        file_obj.write(fh.getvalue())
        file_obj.close()

    def delete_file(self, filename):
        """Delete a file from Google Drive.

        Args:
            filename (str): Name of the file to delete.
        """
        # get file id
        success, fId = self.get_id(filename)

        if success == 0:
            log.warning(f"{filename} not found")
            return

        self.service.files().delete(fileId=fId).execute()

    def get_task(self, task_id):
        """Get the current state of the task."""
        # This method would need to be implemented based on the actual Earth Engine API
        # For now, returning a simple structure
        return {"id": task_id, "state": "COMPLETED"}

    def download_from_task_file(self, task_id, tasks_file, task_filename, sepal_client=None):
        """Download csv file result from GDrive.

        Args:
            task_id (str): id of the task tasked in GEE.
            tasks_file (Path): path file containing all task_id, task_name
            task_filename (str): name of the task file to be downloaded.
        """
        # Check if the task is completed
        task = self.get_task(task_id.strip())

        if task.get("state") == "COMPLETED":
            tmp_result_folder = Path("tmp_results", Path(tasks_file.name).stem)
            if sepal_client:
                tmp_result_folder = sepal_client.get_remote_dir(tmp_result_folder)
            else:
                tmp_result_folder.mkdir(exist_ok=True, parents=True)

            tmp_result_file = tmp_result_folder / task_filename
            self.download_file(task_filename, tmp_result_file, sepal_client)

            return tmp_result_file

        elif task.get("state") == "FAILED":
            raise Exception(f"The task {Path(task_filename).stem} failed.")

        else:
            raise Exception(
                f"The task {Path(task_filename).stem} is not completed yet. "
                f"Current state: {task.get('state')}."
            )
