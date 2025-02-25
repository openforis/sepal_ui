import os
from pathlib import Path, PurePath
from typing import Any, Dict, List, Literal, Optional

import httpx

from sepal_ui.logger.logger import logger

SEPAL_HOST = os.getenv("SEPAL_HOST")
if not SEPAL_HOST:
    raise ValueError("SEPAL_HOST environment variable not set")

VERIFY_SSL = not (SEPAL_HOST == "host.docker.internal" or SEPAL_HOST == "danielg.sepal.io")


class SepalClient:
    def __init__(self, session_id: str, module_name: str):
        """
        Initialize the Sepal HTTP client.

        Args:
            session_id: The session ID for authentication
            base_url: The base URL for the API (optional)
        """
        self.module_name = module_name
        self.BASE_REMOTE_PATH = "/home/sepal-user"
        self.base_url = f"https://{SEPAL_HOST}/api/user-files"
        self.cookies = {"SEPAL-SESSIONID": session_id}
        self.headers = {"Accept": "application/json"}

        # Maybe do a test? and check that the session is valid
        # if not I will get this error:
        # httpx.HTTPStatusError: Client error '401 Unauthorized' for url 'https://danielg.sepal.io/api/user-files/listFiles/?path=%2F&extensions='

        logger.debug("SEPAL_CLIENT: SepalClient initialized")

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

        with httpx.Client(verify=VERIFY_SSL) as client:
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

    def list_files(
        self, folder: str = "/", extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        List files in a specified folder with optional extension filtering.

        Args:
            folder: The folder path to list files from
            extensions: Optional list of file extensions to filter by

        Returns:
            Dict containing the API response
        """
        params = {"path": folder, "extensions": ",".join(extensions or [])}
        return self.rest_call("GET", "listFiles/", params=params)

    def get_file(self, file_path: str) -> bytes:
        """
        Download a file from the specified folder.

        Args:
            folder: Source folder path
            filename: Name of the file to download

        Returns:
            The file content as bytes
        """
        return self.rest_call("GET", "download/", params={"path": self.sanitize_path(file_path)})

    def set_file(self, file_path: str, json_data: str) -> Dict[str, Any]:
        """
        Upload a file to the specified folder.

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

    def sanitize_path(self, file_path: str) -> str:
        path = PurePath(file_path)
        try:
            # Attempt to get a path relative to BASE_REMOTE_PATH
            relative_path = path.relative_to(self.BASE_REMOTE_PATH)
        except ValueError:
            # If file_path isn't under BASE_REMOTE_PATH, keep it as is
            relative_path = path
        return str(relative_path).strip("/")

    def get_remote_dir(self, folder: str, parents: bool = False) -> Path:
        """Create a remote directory and return the Path object."""
        # First ensure the base module results dir exists
        # This is a standard location for module results
        results_path = f"{self.BASE_REMOTE_PATH}/module_results/{self.module_name}"
        self.rest_call(
            "POST",
            "createFolder/",
            params={"path": self.sanitize_path(results_path), "parents": True},
        )

        remote_dir = results_path / Path(folder)
        self.rest_call(
            "POST",
            "createFolder/",
            params={"path": self.sanitize_path(remote_dir), "parents": parents},
        )

        return Path(remote_dir)
