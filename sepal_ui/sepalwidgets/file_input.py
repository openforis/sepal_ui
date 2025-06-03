"""Custom FileInput widget that leverages vuetify templates and handles both local and remote files (sepal)."""

from pathlib import Path
from typing import List as ListType
from typing import Literal, Optional, Union

import ipyvuetify as v
from natsort import natsorted
from pydantic import BaseModel
from traitlets import Bool, Int, List, Unicode

from sepal_ui.logger import logger
from sepal_ui.scripts.sepal_client import SepalClient


class FileDetails(BaseModel):
    name: str
    path: str
    type: Literal["directory", "file"]
    size: int
    modified_time: Optional[float] = 0.0


class ListDirectoryResponse(BaseModel):
    path: str
    files: ListType[FileDetails]

    def sorted(self) -> "ListDirectoryResponse":
        """Returns a new ListDirectoryResponse instance with the files sorted using human sorting, placing directories before files."""
        sorted_files = natsorted(
            self.files, key=lambda x: (0 if x.type == "directory" else 1, x.name.lower())
        )
        return ListDirectoryResponse(path=self.path, files=sorted_files)


def get_local_files(folder: str = "/", extensions: List[str] = [], cache_dirs=None):
    """Get the list of files in a folder on the local machine."""
    files = []
    for file_ in Path(folder).glob("*"):
        if not file_.name.startswith(".") and (
            not extensions or file_.suffix in extensions if file_.is_file() else True
        ):
            files.append(
                FileDetails(
                    name=file_.name,
                    path=str(file_),
                    type="directory" if file_.is_dir() else "file",
                    size=file_.stat().st_size,
                    modified_time=file_.stat().st_mtime,
                )
            )

    return ListDirectoryResponse(path=str(folder), files=files).sorted()


def get_remote_files(sepal_client, folder: str = "/", extensions=None, cache_dirs=None, root="/"):
    """Get the list of files in a folder on the remote server."""
    try:
        response = sepal_client.list_files(folder, extensions=extensions)
        return ListDirectoryResponse.model_validate(response).sorted()

    except Exception as error:
        logger.error(f"Failed to list files: {error}")
        folder_list = []

    return folder_list


class FileInput(v.VuetifyTemplate):

    template_file = Unicode(str(Path(__file__).parent / "vue/FileInput.vue")).tag(sync=True)

    file_list = List([]).tag(sync=True)
    current_folder = Unicode("/").tag(sync=True)
    loading = Bool(False).tag(sync=True)
    extensions = List(Unicode()).tag(sync=True)
    label = Unicode("Select a file").tag(sync=True)
    value = Unicode().tag(sync=True)
    v_model = Unicode().tag(sync=True)
    file = Unicode().tag(sync=True)
    clearable = Bool(True).tag(sync=True)
    error_messages = List([]).tag(sync=True)

    root = Unicode("/").tag(sync=True)

    reload_files = Int(0).tag(sync=True)
    base_path = Unicode("").tag(sync=True)

    def __init__(
        self, initial_folder: str = "", root: str = "", sepal_client: SepalClient = None, **kwargs
    ):
        """Custom widget to select files from the local machine or the sepal server.

        Args:
            initial_folder: The initial folder to read files from.
            root: Maximum root directory that can be accessed.
            sepal_client: Sepal client to access the server.
        """
        super().__init__(**kwargs)
        logger.debug("FileInput initialized")

        self.client = sepal_client
        if sepal_client or initial_folder.startswith(str(Path.home())):
            self.initial_folder = initial_folder
        else:
            self.initial_folder = str(Path.home() / initial_folder)
        logger.debug(f"Initial folder: {self.initial_folder}")
        self.current_folder = self.initial_folder
        self.root = root if root else "" if sepal_client else str(Path.home())

        if not Path(self.current_folder).is_relative_to(self.root):
            raise ValueError(
                f"Initial folder {self.current_folder} is not a subdirectory of {self.root}"
            )

        self.load_files()
        self.observe(self.load_files, "current_folder")
        self.observe(self.load_files, "reload_files")
        self.observe(lambda chg: setattr(self, "v_model", chg["new"]), "value")
        self.observe(lambda chg: setattr(self, "file", chg["new"]), "value")

    def load_files(self, *_):
        """Load the files in the current folder."""
        try:
            self.loading = True

            if not Path(self.current_folder).is_relative_to(self.root):
                raise ValueError(
                    f"Initial folder {self.current_folder} is not a subdirectory of {self.root}"
                )

            if self.client:
                file_list = get_remote_files(
                    self.client,
                    self.current_folder,
                    extensions=self.extensions,
                    cache_dirs=self.file_list,
                    root=self.root,
                )
            else:
                file_list = get_local_files(
                    Path(self.current_folder), extensions=self.extensions, cache_dirs=self.file_list
                )

            # place the parent directory at the top
            if self.current_folder != self.root:
                parent = Path(self.current_folder).parent
                parent = FileDetails(name="..", path=str(parent), type="directory", size=0)
                file_list.files.insert(0, parent)

            self.file_list = file_list.model_dump()["files"]

        except Exception as error:
            logger.error(f"Failed to load files: {error}")
        finally:
            self.loading = False

    def reset(self):
        """Reset the file input widget."""
        self.value = ""
        self.current_folder = self.initial_folder

    def select_file(self, path: Union[str, Path]):
        """Select a file from the list."""
        if self.client:
            raise NotImplementedError("Selecting files is not supported for remote files (yet)")

        file_path = path  # path should be deprecated
        path = Path(file_path)

        # test file existence
        if not path.is_file():
            raise Exception(f"{path} is not a file")

        self.current_folder = file_path.parent
        self.value = str(file_path)
