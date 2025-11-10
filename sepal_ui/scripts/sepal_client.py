"""Client for interacting with sepal userFiles API."""

import os
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Literal, Optional, Union

import httpx

from sepal_ui.logger import log


class SepalClient:
    def __init__(
        self,
        session_id: str,
        module_name: str,
        sepal_host: Optional[str] = None,
        create_base_dir: bool = True,
    ):
        """Initialize the Sepal HTTP client.

        Args:
            session_id: The SEPAL session ID for authentication
            module_name: The name of the module using the client, it creates the module results
                directory if create_base_dir is True.
            sepal_host: Optional SEPAL host, if None uses SEPAL_HOST environment variable
            create_base_dir: If True, creates the base results directory for the module
        """
        self.module_name = module_name
        self.BASE_REMOTE_PATH = "/home/sepal-user"

        # Get SEPAL_HOST environment variable
        self.sepal_host = sepal_host or os.getenv("SEPAL_HOST")
        if not self.sepal_host:
            raise ValueError("SEPAL_HOST environment variable not set")

        # Determine SSL verification based on host
        self.verify_ssl = not (
            self.sepal_host == "host.docker.internal" or self.sepal_host == "danielg.sepal.io"
        )

        self.base_url = f"https://{self.sepal_host}/api/user-files"
        self.cookies = {"SEPAL-SESSIONID": session_id}
        self.headers = {"Accept": "application/json"}

        if create_base_dir:
            self.results_path = self.create_base_dir()
        # Maybe do a test? and check that the session is valid
        # if not I will get this error:
        # httpx.HTTPStatusError: Client error '401 Unauthorized' for url 'https://danielg.sepal.io/api/user-files/listFiles/?path=%2F&extensions='

        log.debug(f"SEPAL_CLIENT: SepalClient initialized, with results path: {self.results_path}")

    def rest_call(
        self,
        method: Literal["GET", "POST", "PUT"],
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[str] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        parse_json: bool = True,
    ) -> Union[Dict[str, Any], bytes]:
        """Make HTTP requests and handle JSON/binary responses."""
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

            # Handle 409 Conflict for createFolder and setFile endpoints
            # This means the resource already exists and cannot be overwritten
            if response.status_code == 409 and endpoint.rstrip("/") in ["createFolder", "setFile"]:
                log.debug(
                    f"Resource already exists for {endpoint} (409 Conflict) - continuing normally"
                )
                # Return empty dict for JSON responses or empty bytes for binary
                return {} if parse_json else b""

            response.raise_for_status()

            if parse_json:
                return response.json()
            else:
                return response.content

    def create_base_dir(self) -> PurePosixPath:
        """Create the base results directory and return the PurePosixPath object."""
        results_path = f"{self.BASE_REMOTE_PATH}/module_results/{self.module_name}"
        try:
            self.rest_call(
                "POST",
                "createFolder/",
                params={"path": self.sanitize_path(results_path), "recursive": True},
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                log.debug(
                    f"Folder already exists: {results_path} (403 Forbidden) - continuing normally"
                )
            else:
                raise

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

    def get_file(self, file_path: str, parse_json=False) -> bytes:
        """Download a file from the specified folder.

        Args:
            file_path: The file path to download
            parse_json: If True, parse the response as JSON; otherwise return raw bytes

        Returns:
            The file content as bytes
        """
        return self.rest_call(
            "GET",
            "download/",
            params={"path": self.sanitize_path(file_path)},
            parse_json=parse_json,
        )

    def set_file(
        self, file_path: str, content: Union[str, bytes], overwrite: bool = False
    ) -> Dict[str, Any]:
        """Upload any content (text or binary) via multipart/form-data.

        Args:
            file_path: The path where the file will be saved on the server
            content: The content to upload, can be a string or bytes
            overwrite: If True, allows overwriting existing files on the server

        """
        # ensure we have bytes
        if isinstance(content, str):
            payload = content.encode("utf-8")
        else:
            payload = content

        params = {"path": self.sanitize_path(file_path), "overwrite": str(overwrite).lower()}

        # pick MIME by extension
        ext = Path(file_path).suffix.lower()
        mime_map = {
            ".json": "application/json",
            ".csv": "text/csv",
            ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ".xls": "application/vnd.ms-excel",
            ".tif": "image/tiff",
            ".tiff": "image/tiff",
        }
        mime = mime_map.get(ext, "application/octet-stream")

        files = {"file": (Path(file_path).name, payload, mime)}

        return self.rest_call("POST", "setFile/", params=params, files=files)

    def sanitize_path(self, file_path: Union[str, Path]) -> PurePosixPath:
        """Sanitize a file path to be relative to the base remote path."""
        p = PurePosixPath(str(file_path))
        base = PurePosixPath(self.BASE_REMOTE_PATH)

        if p.is_absolute():
            try:
                rel = p.relative_to(base)
            except ValueError:
                raise ValueError(f"sanitize_path: expected absolute under {base!r}, got {p!r}")
            if ".." in rel.parts:
                raise ValueError(f"sanitize_path: path traversal detected: {p!r}")
            return rel

        if ".." in p.parts:
            raise ValueError(f"sanitize_path: path traversal detected: {p!r}")
        return p

    def get_remote_dir(self, folder: Union[str, Path], parents: bool = False) -> PurePosixPath:
        """Create a remote directory and return its sanitized path."""
        sanitized_folder = self.sanitize_path(folder)
        self.rest_call(
            "POST",
            "createFolder/",
            params={"path": sanitized_folder, "recursive": parents},
        )
        return sanitized_folder
