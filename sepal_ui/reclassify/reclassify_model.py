"""
Model object dedicated to the reclassification interface.
"""

from pathlib import Path
from typing import Any, Optional, Union

import ee
import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio as rio
import traitlets as t
from matplotlib.colors import to_rgba
from natsort import natsorted
from rasterio.windows import from_bounds
from typing_extensions import Self

from sepal_ui import aoi
from sepal_ui.message import ms
from sepal_ui.model import Model
from sepal_ui.scripts import decorator as sd
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su

from .parameters import NO_VALUE

__all__ = ["ReclassifyModel"]


class ReclassifyModel(Model):

    band: t.Any = t.Any(None).tag(sync=True)
    "the band name or number to use for the reclassification if raster type. Use property name if vector type"

    src_local: t.Any = t.Any(None).tag(sync=True)
    "the source file to reclassify (from a local path) only used if :code:`gee=False`"

    src_gee: t.Unicode = t.Unicode(None, allow_none=True).tag(sync=True)
    "AssetId of the used input asset for reclassification. Only used if :code:`gee=True`"

    dst_class_file: t.Any = t.Any(None).tag(sync=True)
    "the destination file for reclassify matrix"

    dst_dir: Union[Path, str] = ""
    "the dir used to store the output"

    gee: t.Bool = t.Bool(False).tag(sync=True)
    "either to use the gee backend or not"

    aoi_model: Optional[aoi.AoiModel] = None
    "AOI model object to get an area of interest if one is selected"

    folder: str = ""
    "the init GEE asset folder where the asset selector should start looking (debugging purpose)"

    enforce_aoi: bool = False
    "either or not an aoi should be set to allow the reclassification"

    # data manipulation
    matrix: t.Dict = t.Dict({}).tag(sync=True)
    "the transfer matrix between the input and the output using the following format: {old_value: new_value, ...}"

    # outputs
    input_type: t.Bool = t.Bool(False).tag(sync=True)  # 1 raster, 0 vector
    "the input type, 1 for raster and 0 for vector"

    src_class: t.Dict = t.Dict({}).tag(sync=True)
    "the source classes using the following columns: {code: (desc, color)}"

    dst_class: t.Dict = t.Dict({}).tag(sync=True)
    "the destination classes using the following columns: {code: (desc, color)}"

    dst_local: t.Unicode = t.Unicode(None, allow_none=True).tag(sync=True)
    "the output file. default to :code:`dst_dir/f'{src_local.stem}_reclass.{src_local.suffix}'`"

    dst_gee: t.Unicode = t.Unicode(None, allow_none=True).tag(sync=True)
    "the output assetId. default to :code:`dst_dir/f'{src_gee.stem}_reclass'`"

    # Create a state var, to determine if an asset has been remaped
    remaped: t.Int = t.Int(0).tag(sync=True)
    "state var updated each time an input is remapped"

    save: bool = False
    "either or not the relcassified dataset need to be saved"

    dst_local_memory: Any = None
    "the local output of the reclassification"

    dst_gee_memory: Any = None
    "the gee output of the reclassification"

    table_created: t.Bool = t.Bool(False).tag(sync=True)
    "either or not a table have been created"

    def __init__(
        self,
        gee: bool = False,
        dst_dir: Union[Path, str] = Path.home(),
        aoi_model: Optional[aoi.AoiModel] = None,
        folder: str = "",
        save: bool = True,
        enforce_aoi: bool = False,
        **kwargs,
    ) -> None:
        """
        Reclassification model to store information about the current reclassification and share them within your app.

        Save all the input and output of the reclassification + the the matrix to move from one to another. It is embeding 2 backends, one based on GEE that will use assets as in/out and another based on python that will use local files as in/out. The model can handle both vector and raster data, the format and name of the output will be determined from the the input format/name. The developer will still have the possiblity to choose where to save the outputs (folder name).

        Args:
            gee: either or not to set :code:`gee` to True
            dst_dir: the destination forlder for outputs
            folder: the init GEE asset folder where the asset selector should start looking (debugging purpose)
            aoi_model: the aoi model to link to the reclassify workflow
            enforce_aoi: either or not an aoi should be set to allow the reclassification
        """
        # init the model
        super().__init__(**kwargs)

        # save the folder where the results should be stored
        # only used for local export
        self.dst_dir = Path(dst_dir)

        # save relation with gee
        self.gee = gee

        if self.gee:
            su.init_ee()

        if self.gee:
            self.folder = str(folder) or ee.data.getAssetRoots()[0]["id"]
        else:
            self.folder = None

        self.aoi_model = aoi_model

        # aoi_model and reclassify model must be aligned when it comes to gee
        if self.aoi_model:
            if self.aoi_model.gee != self.gee:
                raise Exception(
                    "Both aoi_model.gee and self.gee parameters has to be equals."
                    + f"Received {self.aoi_model.ee} for aoi_model and {self.gee} for reclassify_model."
                )

        self.enforce_aoi = enforce_aoi

        # set if the model need to save by default
        self.save = save

    def get_classes(self) -> dict:
        """
        Extract the classes from the class file.

        The class file need to be compatible with the reclassify tool i.e. a table file with 3 headerless columns using the following format: 'code', 'desc', 'color'. Color need to be set in hexadecimal to be read else black will be used.

        Returns:
            the dict of the classes using following format: {code: (name, color)}
        """
        file = self.dst_class_file

        if not file:
            raise AttributeError("missing file")

        path = Path(file)
        if not path.is_file():
            raise Exception(f"{file} is not existing")

        df = pd.read_csv(file, header=None)

        # dst_class_file should be set on the model csv output of the custom view
        # 3 column: 1: code, 2: name, 3: color
        df = df.rename(columns={0: "code", 1: "desc", 2: "color"})

        # save the df for reclassify usage
        class_list = {row.code: (row.desc, row.color) for _, row in df.iterrows()}

        # create a dict out of it
        return class_list

    def get_type(self) -> bool:
        """
        Guess the type of the input and set the input type attribute for the model (vector or raster).

        Returns:
            the type of input (1 for raster, 0 for vector)
        """
        if self.gee:
            if not self.src_gee:
                raise Exception("Missing gee input")

            asset_info = ee.data.getAsset(self.src_gee)["type"]

            if asset_info == "TABLE":
                self.input_type = False
            elif asset_info == "IMAGE":
                self.input_type = True
            else:
                raise AttributeError(f"Unrecognized asset type: {asset_info}")
        else:
            if not self.src_local:
                raise Exception("no input")

            input_path = Path(self.src_local)

            if input_path.suffix in [".geojson", ".shp"]:
                self.input_type = False
            elif input_path.suffix in [".tif", ".tiff", ".vrt"]:
                self.input_type = True
            else:
                raise AttributeError(f"Unrecognized file format: {input_path.suffix}")
        return self.input_type

    def get_bands(self) -> list:
        """
        Use the input_type to extract all the bands/properties from the input.

        Returns:
            sorted list of all the available bands/properties as
            integer or str
        """

        @sd.need_ee
        def _ee_image():

            return ee.Image(self.src_gee).bandNames().getInfo()

        @sd.need_ee
        def _ee_vector():

            columns = ee.FeatureCollection(self.src_gee).first().getInfo()["properties"]

            return (
                str(c)
                for c in columns.keys()
                if c not in ["system:index", "Shape_Area"]
            )

        def _local_image():

            with rio.open(self.src_local) as f:
                bands = [i for i in range(1, f.count + 1)]

            return bands

        def _local_vector():

            df = gpd.read_file(self.src_local)

            return [c for c in df.columns.tolist() if c != "geometry"]

        # map all the function in the guess matrix (gee, type)
        band_func = [[_local_vector, _local_image], [_ee_vector, _ee_image]]

        # return the selected function
        # remember to use self as a parameter
        return natsorted(band_func[self.gee][self.input_type]())

    def get_aoi(self) -> Union[gpd.GeoDataFrame, ee.ComputedObject]:
        """
        Validate and get feature collection from aoi_model.

        Returns:
            the saved AOI in the appropriate format
        """
        # by default it's none
        aoi = None

        # return None if no aoi_model is selected
        if not self.aoi_model:
            return

        # return none if no aoi is selected
        # test gdf as it's set whatever the type of AoiModel (gee or not)
        if self.aoi_model.gdf is None:
            if self.enforce_aoi:
                raise Exception("You have to select an area of interest before")

        else:  # return the aoi as a vector
            if self.gee:
                aoi = self.aoi_model.feature_collection
            else:
                aoi = self.aoi_model.gdf

        return aoi

    def unique(self) -> dict:
        """
        Retreive all the existing class.

        Retreive all the existing class from the specified band/property according to the input_type. The data will be saved in self.src_class with no_name and black as a color.

        Returns:
            the unique class value found in the specified band/property and there color/name defaulted to none and black
        """
        if not self.band:
            raise Exception("You need to provide a band/property to reclassify.")

        @sd.need_ee
        def _ee_image():

            # reduce the image
            image = ee.Image(self.src_gee).select(self.band)
            aoi = self.get_aoi() or image
            geometry = aoi.geometry()

            reduction = image.reduceRegion(
                ee.Reducer.frequencyHistogram(), geometry, maxPixels=1e13
            )

            # Remove all the unnecessary reducer output structure and make a
            # list of values.
            values = (
                ee.Dictionary(reduction.get(image.bandNames().get(0))).keys().getInfo()
            )

            return values

        @sd.need_ee
        def _ee_vector():

            collection = ee.FeatureCollection(self.src_gee)
            aoi = self.get_aoi() or collection
            geometry = aoi.geometry()

            # get the feature
            values = (
                collection.filterBounds(geometry).aggregate_array(self.band).getInfo()
            )

            return list(set(values))

        def _local_image():

            with rio.open(self.src_local) as src:

                bounds = self.get_aoi().total_bounds if self.get_aoi() else src.bounds
                data = src.read(
                    self.band, window=from_bounds(*bounds, transform=src.transform)
                )
                count = np.bincount(data.flatten())

            return np.nonzero(count != 0)[0].tolist()

        def _local_vector():

            gdf = gpd.read_file(self.src_local)
            bounds = self.get_aoi().total_bounds if self.get_aoi() else gdf.total_bounds
            xmin, ymin, xmax, ymax = bounds
            gdf = gdf.cx[xmin:xmax, ymin:ymax]

            return gdf[self.band].unique().tolist()

        # map all the function in the guess matrix (gee, type)
        unique_func = [[_local_vector, _local_image], [_ee_vector, _ee_image]]

        # get values from the selected func
        # remember to use self as a parameter
        values = natsorted(unique_func[self.gee][self.input_type]())

        # create the init dictionnary
        self.src_class = {v: ("no_name", "#000000") for v in values}

        return self.src_class

    def reclassify(self) -> Self:
        """
        Reclassify the input according to the provided matrix.

        For vector file type reclassifying correspond to add an extra column at the end, for raster the initial class band will be replaced by the new class, the oher being kept unmodified. vizualization colors will be set for both local (QGIS compatible) and assets (SEPAL vizualization compatible).
        """
        if not self.matrix:
            raise Exception(
                "You need a reclassification matrix to reclassify an asset."
            )
        if not self.band:
            raise Exception("You need to provide a band/property to reclassify.")

        @sd.need_ee
        def _ee_image():

            if not self.src_gee:
                raise Exception("You need to provide source asset.")

            # create the asset description
            self.set_dst_gee()

            # load the image
            # remap according to the matrix
            from_, to_ = list(zip(*matrix.items()))

            image = ee.Image(self.src_gee)
            aoi = self.get_aoi() or image
            geometry = aoi.geometry()

            ee_image = (
                image.clip(geometry)
                .remap(from_, to_, 0, self.band)
                .select(["remapped"], [self.band])
            )

            # gather all the other band in the image
            # ee_image = ee.Image(self.src_gee).addBands(ee_image, overwrite=True)

            # add colormapping parameters
            # set return an element so we force cast it to ee.Image
            code, desc, color = ["0"], ["no_data"], ["#000000"]
            for k, v in self.dst_class.items():
                code.append(str(k))
                desc.append(str(v[0]))
                color.append(str(v[1]))

            ee_image = ee.Image(
                ee_image.set(
                    {
                        "visualization_0_name": "Classification",
                        "visualization_0_bands": self.band,
                        "visualization_0_type": "categorical",
                        "visualization_0_labels": ",".join(desc),
                        "visualization_0_palette": ",".join(color),
                        "visualization_0_values": ",".join(code),
                    }
                )
            )

            # save the file in a in_memeory variable
            self.dst_gee_memory = ee_image

            if self.save:

                # export
                params = {
                    "image": ee_image,
                    "assetId": self.dst_gee,
                    "description": Path(self.dst_gee).stem,
                    "scale": ee_image.projection().nominalScale().getInfo(),
                    "maxPixels": 1e13,
                    "pyramidingPolicy": {".default": "mode"},
                }

                task = ee.batch.Export.image.toAsset(**params)
                task.start()

            return self.dst_gee

        @sd.need_ee
        def _ee_vector():

            if not self.src_gee:
                raise Exception("You need to provide source asset.")

            # create the asset description
            self.set_dst_gee()

            # add a new propertie

            def add_prop(feat):
                """Add reclass column to the new feature."""
                index = ee_from.indexOf(feat.get(self.band))
                # if search value is not in from, -1 is returned
                new_val = ee.Algorithms.If(index.eq(-1), NO_VALUE, ee_to.get(index))
                return feat.set({"reclass": new_val})

            ee_matrix = ee.List(list(matrix.items())).unzip()
            ee_from, ee_to = ee.List(ee_matrix.get(0)), ee.List(ee_matrix.get(1))

            collection = ee.FeatureCollection(self.src_gee)
            aoi = self.get_aoi() or collection
            geometry = aoi.geometry()

            self.dst_gee_memory = (
                ee.FeatureCollection(self.src_gee).filterBounds(geometry).map(add_prop)
            )

            # add colormapping parameters

            if self.save:

                # export
                params = {
                    "collection": self.dst_gee_memory,
                    "assetId": self.dst_gee,
                    "description": Path(self.dst_gee).stem,
                }

                task = ee.batch.Export.table.toAsset(**params)
                task.start()

            return self.dst_gee

        def _local_image():

            if not self.src_local:
                raise Exception("You need to provide source asset.")

            # set the output file
            self.dst_local = str(
                self.dst_dir / f"{Path(self.src_local).stem}_reclass.tif"
            )

            with rio.open(self.src_local) as src:

                bounds = self.get_aoi().total_bounds if self.get_aoi() else src.bounds
                window = from_bounds(*bounds, transform=src.transform)
                raw = src.read(self.band, window=window)

                data = np.zeros_like(raw, dtype=np.int64)

                for old_val, new_val in matrix.items():
                    data += (raw == old_val) * new_val

                if self.save:

                    profile = src.profile
                    profile.update(
                        driver="GTiff",
                        count=1,
                        compress="lzw",
                        dtype=np.uint8,
                        height=window.height,
                        width=window.width,
                        transform=src.window_transform(window),
                    )

                    with rio.open(self.dst_local, "w", **profile) as dst:
                        dst.write(data.astype(np.uint8), 1, window=window)

                        # add the colors to the image
                        colormap = {0: (0, 0, 0)}
                        for code, item in self.dst_class.items():
                            colormap[code] = tuple(
                                int(c * 255) for c in to_rgba(item[1])
                            )
                        dst.write_colormap(self.band, colormap)

                    # Save raster in memory
                    self.dst_local_memory = data

            return self.dst_local

        def _local_vector():

            if not self.src_local:
                raise Exception("You need need to provide source asset.")

            # set the output file
            self.dst_local = str(
                self.dst_dir / f"{Path(self.src_local).stem}_reclass.shp"
            )

            # read the dataset
            gdf = gpd.read_file(self.src_local)
            bounds = self.get_aoi().total_bounds if self.get_aoi() else gdf.total_bounds
            xmin, ymin, xmax, ymax = bounds
            gdf = gdf.cx[xmin:xmax, ymin:ymax]

            # map the new column
            gdf["reclass"] = gdf.apply(lambda row: matrix[row[self.band]], axis=1)

            # add the colors to the gdf
            # waiting for an answer there :
            # https://gis.stackexchange.com/questions/404946/how-can-i-save-my-geopandas-symbology
            self.dst_local_memory = gdf

            # save the file
            if self.save:

                gdf.to_file(self.dst_local)

            return self.dst_local

        # map all the function in the guess matrix (gee, type)
        reclassify_func = [[_local_vector, _local_image], [_ee_vector, _ee_image]]

        # reshape the matrix so that every value correspond to 1 key
        # Cast np.int64 to int
        matrix = {int(k): int(v) for k, v in self.matrix.items()}

        # return the selected function
        # remember to use self as a parameter
        res = reclassify_func[self.gee][self.input_type]()

        # tell the rest of the apps that a reclassification is finished
        self.remaped += 1

        if self.save:
            return ms.rec.rec.export[self.gee][self.input_type].format(res)

        return "Asset successfully reclassified."

    def set_dst_gee(self) -> str:
        """
        Creates a unique and consecutive asset name based on the source.

        Returns:
            the destination folder
        """
        # create the asset_id
        asset_name = f"{Path(self.src_gee).stem}_reclass"

        # impossible to guess the folder as an asset name can start with:
        # project/earthengin-legacy/users/xx/xx/....
        # users/xx/xx/xx
        # OXFORD/xx/xx/xx for public dataset
        # fallback to the root folder
        dst_gee = str(Path(self.folder, asset_name))

        # check if the name already exist
        current_assets = [asset["name"] for asset in gee.get_assets(self.folder)]

        # An user could reclassify twice an asset,
        # So let's create an unique name
        while dst_gee in current_assets:
            dst_gee = su.next_string(dst_gee)

        # set the dst_gee of the model
        self.dst_gee = dst_gee

        return self
