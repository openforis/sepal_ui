"""Client for interacting with sepal userFiles API."""

import os
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Literal, Optional

import httpx

from sepal_ui.logger import logger


class SepalClient:
    def __init__(self, session_id: str, module_name: str):
        """Initialize the Sepal HTTP client.

        Args:
            session_id: The SEPAL session ID for authentication
            module_name: The name of the module using the client, it creates the module results directory.
        """
        self.module_name = module_name
        self.BASE_REMOTE_PATH = "/home/sepal-user"

        # Get SEPAL_HOST environment variable
        self.sepal_host = os.getenv("SEPAL_HOST")
        if not self.sepal_host:
            raise ValueError("SEPAL_HOST environment variable not set")

        # Determine SSL verification based on host
        self.verify_ssl = not (
            self.sepal_host == "host.docker.internal" or self.sepal_host == "danielg.sepal.io"
        )

        self.base_url = f"https://{self.sepal_host}/api/user-files"
        self.cookies = {"SEPAL-SESSIONID": session_id}
        self.headers = {"Accept": "application/json"}

        self.results_path = self.create_base_dir()
        # Maybe do a test? and check that the session is valid
        # if not I will get this error:
        # httpx.HTTPStatusError: Client error '401 Unauthorized' for url 'https://danielg.sepal.io/api/user-files/listFiles/?path=%2F&extensions='

        logger.debug(
            f"SEPAL_CLIENT: SepalClient initialized, with results path: {self.results_path}"
        )

    def rest_call(
        self,
        method: Literal["GET", "POST", "PUT"],
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Helper method to make HTTP requests."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        with httpx.Client(verify=self.verify_ssl) as client:
            response = client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                cookies=self.cookies,
                headers=self.headers,
                files=files,
                data=data,
            )
            response.raise_for_status()
            return response.json()

    def create_base_dir(self) -> PurePosixPath:
        """Create the base results directory and return the PurePosixPath object."""
        results_path = f"{self.BASE_REMOTE_PATH}/module_results/{self.module_name}"
        self.rest_call(
            "POST",
            "createFolder/",
            params={"path": self.sanitize_path(results_path), "recursive": True},
        )

        return PurePosixPath(results_path)

    def list_files(
        self, folder: str = "/", extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """List files in a specified folder with optional extension filtering.

        Args:
            folder: The folder path to list files from
            extensions: Optional list of file extensions to filter by

        Returns:
            Dict containing the API response
        """
        params = {"path": folder, "extensions": ",".join(extensions or [])}
        return self.rest_call("GET", "listFiles/", params=params)

    def get_file(self, file_path: str) -> bytes:
        """Download a file from the specified folder.

        Args:
            file_path: The file path to download

        Returns:
            The file content as bytes
        """
        return self.rest_call("GET", "download/", params={"path": self.sanitize_path(file_path)})

    def set_file(self, file_path: str, json_data: str) -> Dict[str, Any]:
        """Upload a file to the specified folder.

        Args:
            folder: Destination folder path
            file_content: The file content as bytes
            file_path: Name for the uploaded file

        Returns:
            Dict containing the API response
        """
        data = {"file": json_data}

        return self.rest_call(
            "POST",
            "setFile/",
            params={"path": self.sanitize_path(file_path)},
            data=data,
        )

    def sanitize_path(self, file_path: str | Path) -> str:
        """Sanitize a file path to be relative to the base remote path."""
        path = PurePosixPath(str(file_path))
        base_path = PurePosixPath(self.BASE_REMOTE_PATH)

        try:
            # Attempt to get a path relative to BASE_REMOTE_PATH
            relative_path = path.relative_to(base_path)
        except ValueError:
            # If file_path isn't under BASE_REMOTE_PATH, keep it as is
            relative_path = path
        return str(relative_path).strip("/")

    def get_remote_dir(self, folder: str, parents: bool = False) -> PurePosixPath:
        """Create a remote directory and return the PurePosixPath object."""
        remote_dir = PurePosixPath(self.results_path) / PurePosixPath(folder)
        self.rest_call(
            "POST",
            "createFolder/",
            params={"path": self.sanitize_path(remote_dir), "recursive": parents},
        )

        return remote_dir
