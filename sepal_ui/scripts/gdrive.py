import io
from pathlib import Path

import ee
from apiclient import discovery
from googleapiclient.http import MediaIoBaseDownload
from osgeo import gdal

from sepal_ui.scripts import utils as su

################################################################################
# attributes of the singleton
#

# call need_ee for the whole file
su.init_ee()

SERVICE = discovery.build(
    serviceName="drive",
    version="v3",
    cache_discovery=False,
    credentials=ee.credentials(),
)
"the gdrive service used to access the content of the user folder"

################################################################################
# functions
#


def get_all_items(mime_type="image/tiff"):
    """
    get all the items in the Gdrive, items will have 2 columns, 'name' and 'id'.
    It excludes files that are contained in the trashbin.

    Args:
        mime_type (str, optional): the mime type to look for by default Tif images

    Return:
        (list): the found items with 2 columns ('id' and 'name')
    """

    # get list of files
    return (
        SERVICE.files()
        .list(
            q=f"mimeType='{mime_type}' and trashed = false",
            pageSize=1000,
            fields="nextPageToken, files(id, name)",
        )
        .execute()
        .get("files", [])
    )


def get_items(file_name, mime_type="image/tiff"):
    """
    look for the file_name patern in user Gdrive files and retreive a list of Ids.

    usually gee export your files using a tiling system so the file name provided
    need to be the one from the export description.

    Args:
        file_name (str): the file name used during the exportation step
        mime_type (str, optional): the mime type to look for by default Tif images

    Return:
        (list): the list of file id corresponding to the requested filename in your gdrive account
    """

    return [i for i in get_items(mime_type) if i["name"].startswith(file_name)]


def delete_items(items):
    """
    Delete the items from Gdrive

    Args:
        items (list): the list of item to delete as described in get_imes functions
    """

    for i in items:
        SERVICE.files().delete(fileId=i["id"]).execute()

    return


def download_items(file_name, local_path, mime_type="image/tiff", delete=False):
    """
    Download from Gdrive all the file corresponding to an equivalent get_items request.

    if the mime_type is "image/tiff" a vrt file will be created. The delete option will automatically delete files once they are dowloaded.

    Args:
        file_name (str): the file name used during the exportation step
        local_path (pathlike object): the destination of the files
        mime_type (str, optional): the mime type to look for by default Tif images
        delete (bool, optional): either or not the file need to be deleted once the download is finished. default to :code:`False`

    Return:
        (pathlib.Path): the path to the download folder or the path to the vrt
    """

    # cast as path
    local_path = Path(local_path)

    # get the items
    items = get_items(file_name, mime_type)

    # load them to the use workspace
    local_files = []
    for i in items:
        request = SERVICE.files().get_media(fileId=i["id"])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        # download in chunks
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        # write to files
        local_file = local_path / i["name"]
        with local_file.open("wb") as fo:
            fo.write(fh.getvalue())

        local_files.append(local_file)

    # delete the items ?
    delete is False or delete_items(items)

    # create a vrt ?
    if mime_type == "image/tiff":
        vrt_file = local_path / f"{file_name}.vrt"
        ds = gdal.BuildVRT(str(vrt_file), [str(f) for f in local_files])

        # if there is no cache to empty it means that one of the dataset was empty
        try:
            ds.FlushCache()
        except AttributeError:
            raise Exception("one of the dataset was empty")

        # check that the file was effectively created (gdal doesn't raise errors)
        if not vrt_file.is_file():
            raise Exception(f"the vrt {vrt_file} was not created")

    return vrt_file if mime_type == "image/tiff" else local_path
