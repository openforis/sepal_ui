import ee
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile

from sepal_ui import aoi
from sepal_ui import sepalwidgets as sw


class TestAoiModel:

    # test folder
    FOLDER = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"

    def test_init(self):

        # dummy alert
        alert = sw.Alert()

        # default init
        aoi_model = aoi.AoiModel(alert, folder=self.FOLDER)
        assert isinstance(aoi_model, aoi.AoiModel)
        assert aoi_model.ee == True

        # with default assetId
        asset_id = "users/bornToBeAlive/sepal_ui_test/italy"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)

        assert aoi_model.asset_name == asset_id
        assert aoi_model.default_asset == asset_id
        assert all(aoi_model.gdf) != None
        assert aoi_model.feature_collection != None
        assert aoi_model.name == "italy"

        # with a default admin
        admin = 85  # GAUL France
        aoi_model = aoi.AoiModel(alert, admin=admin, folder=self.FOLDER)
        assert aoi_model.name == "FRA"

        # with a default vector
        vector = self._create_fake_vector()
        aoi_model = aoi.AoiModel(alert, vector=vector, gee=False)
        assert aoi_model.name == "gadm36_VAT_0"

        [f.unlink() for f in Path("~").expanduser().glob(f"{vector.stem}.*")]

        # test with a non ee definition
        admin = "FRA"  # GADM France
        aoi_model = aoi.AoiModel(alert, gee=False, admin=admin, folder=self.FOLDER)

        assert aoi_model.name == "FRA"

        return

    def test_get_columns(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)

        # test data
        test_data = [
            "ADM0_CODE",
            "ADM0_NAME",
            "DISP_AREA",
            "EXP0_YEAR",
            "STATUS",
            "STR0_YEAR",
            "Shape_Leng",
        ]

        res = aoi_model.get_columns()

        assert res == test_data

        return

    def test_get_fields(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)
        column = "ADM0_CODE"

        res = aoi_model.get_fields(column)

        assert res == [85]

        return

    def test_get_selected(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)
        ee_france = ee.FeatureCollection(asset_id)

        # select the geometry associated with france (all of it)
        column = "ADM0_CODE"
        field = 85

        feature = aoi_model.get_selected(column, field)

        feature_geom = feature.geometry().getInfo()
        france_geom = ee_france.geometry().getInfo()

        assert feature_geom == france_geom

        return

    def test_clear_attributes(self):

        # dummy alert
        alert = sw.Alert()

        aoi_model = aoi.AoiModel(alert, folder=self.FOLDER)

        dum = "dum"

        # insert dum parameter everywhere
        aoi_model.method = dum
        aoi_model.point_json = dum
        aoi_model.vector_json = dum
        aoi_model.geo_json = dum
        aoi_model.admin = dum
        aoi_model.asset_name = dum
        aoi_model.name = dum
        aoi_model.gdf = dum
        aoi_model.feature_collection = dum
        aoi_model.ipygeojson = dum

        # clear them
        aoi_model.clear_attributes()

        assert aoi_model.method == None
        assert aoi_model.point_json == None
        assert aoi_model.vector_json == None
        assert aoi_model.geo_json == None
        assert aoi_model.admin == None
        assert aoi_model.asset_name == None
        assert aoi_model.name == None
        assert aoi_model.gdf == None
        assert aoi_model.feature_collection == None
        assert aoi_model.ipygeojson == None
        assert aoi_model.default_asset == None
        assert aoi_model.default_admin == None
        assert aoi_model.default_vector == None

        # check that default are saved
        aoi_model = aoi.AoiModel(alert, admin=85, folder=self.FOLDER)  # GAUL for France

        # insert dummy args
        aoi_model.method = dum
        aoi_model.point_json = dum
        aoi_model.vector_json = dum
        aoi_model.geo_json = dum
        aoi_model.admin = dum
        aoi_model.asset_name = dum
        aoi_model.name = dum
        aoi_model.gdf = dum
        aoi_model.feature_collection = dum
        aoi_model.ipygeojson = dum

        # clear
        aoi_model.clear_attributes()

        # assert that it's still france
        assert aoi_model.name == "FRA"

        return

    def test_total_bounds(self):

        # dummy alert
        alert = sw.Alert()

        # init
        asset_id = "users/bornToBeAlive/sepal_ui_test/france"
        aoi_model = aoi.AoiModel(alert, asset=asset_id, folder=self.FOLDER)

        # test data
        expected_bounds = (
            -5.142230921252722,
            41.33878298628808,
            9.561552263332496,
            51.09281241936492,
        )

        bounds = aoi_model.total_bounds()

        assert bounds == expected_bounds

        return

    def _create_fake_vector(self):

        # download vatican city from GADM
        root_dir = Path("~").expanduser()
        file = root_dir / "test.zip"

        gadm_vat_link = "https://biogeo.ucdavis.edu/data/gadm3.6/shp/gadm36_VAT_shp.zip"
        name = "gadm36_VAT_0"

        urlretrieve(gadm_vat_link, file)

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(root_dir)

        file.unlink()

        return root_dir / f"{name}.shp"


from traitlets import Unicode, Any, Dict, List, Bool, Int
from pathlib import Path

import pandas as pd
import geopandas as gpd
import numpy as np
import rasterio as rio

from .parameters import *
from sepal_ui.model import Model
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su
from matplotlib.colors import to_rgba


import ee


class TestReclassifyModel(Model):

    dst_dir = str(Path("~").expanduser() / "tmp")

    def test_init(self):

        alert = sw.Alert()
        aoi_model = aoi.AoiModel(alert, folder=self.dst_dir)

        assert isinstance(aoi_model, aoi.AoiModel)
        assert isinstance(gee, bool)
        assert isinstance(save, bool)

    def save_matrix(self, filename):
        """
        Save the matrix i a csv file

        Return:
            self
        """

        if not len(self.matrix):
            return self

        df = pd.Dataframe(
            {
                "src": [c for c in self.matrix.keys()],
                "dst": [c for c in self.matrix.values()],
            }
        )
        df.to_csv(filename)

        return self

    @staticmethod
    def get_classes(file):
        """
        Extract the classes from the class file. The class file need to be compatible with the reclassify tool i.e. a table file with 3 headerless columns using the following format: 'code', 'desc', 'color'. Color need to be set in hexadecimal to be read else black will be used.

        Args:
            file (pathlike object): the pathlib object of the class file

        Return:
            (dict): the dict of the classes using following format:
                {code: (name, color)}
        """

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

    def get_type(self):
        """
        Guess the type of the input and set the input type attribute for the model (vector or raster)

        Return:
            (bool): the type of input (1 for raster, 0 for vector)
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

    def get_bands(self):
        """
        Use the input_type to extract all the bands/properties from the input

        Return:
            (list): sorted list of all the available bands/properties as
            integer or str
        """

        @su.need_ee
        def _ee_image():

            return sorted(ee.Image(self.src_gee).bandNames().getInfo())

        @su.need_ee
        def _ee_vector():

            columns = ee.FeatureCollection(self.src_gee).first().getInfo()["properties"]

            return sorted(
                str(c)
                for c in columns.keys()
                if c not in ["system:index", "Shape_Area"]
            )

        def _local_image():

            with rio.open(self.src_local) as f:
                bands = [i for i in range(1, f.count + 1)]

            return sorted(bands)

        def _local_vector():

            df = gpd.read_file(self.src_local)

            return [c for c in df.columns.tolist() if c != "geometry"]

        # map all the function in the guess matrix (gee, type)
        band_func = [[_local_vector, _local_image], [_ee_vector, _ee_image]]

        # return the selected function
        # remember to use self as a parameter
        return band_func[self.gee][self.input_type]()

    def get_aoi(self):
        """Validate and get feature collection from aoi_model"""

        # TODO: Validate if the aoi is within the bounds of the inputs

        if self.aoi_model:
            if not self.aoi_model.feature_collection:
                raise Exception("You have to select an area of interest before")
            else:
                return self.aoi_model.feature_collection.geometry()

    def unique(self):
        """
        Retreive all the existing class from the specified band/property according to the input_type.
        The data will be saved in self.src_class with no_name and black as a color.

        Return:
            (Dict): the unique class value found in the specified band/property
            and there color/name defaulted to none and black
        """

        @su.need_ee
        def _ee_image():

            # reduce the image
            image = ee.Image(self.src_gee).select(self.band)
            geometry = image.geometry() if not self.aoi_model else self.get_aoi()
            reduction = image.reduceRegion(
                ee.Reducer.frequencyHistogram(), geometry, maxPixels=1e13
            )

            # Remove all the unnecessary reducer output structure and make a
            # list of values.
            values = (
                ee.Dictionary(reduction.get(image.bandNames().get(0))).keys().getInfo()
            )

            return values

        @su.need_ee
        def _ee_vector():

            if self.aoi_model:
                geometry = self.get_aoi()

                # get the feature
                values = (
                    ee.FeatureCollection(self.src_gee)
                    .filterBounds(geometry)
                    .aggregate_array(self.band)
                    .getInfo()
                )
            else:
                values = (
                    ee.FeatureCollection(self.src_gee)
                    .aggregate_array(self.band)
                    .getInfo()
                )
            return list(set(values))

        def _local_image():

            with rio.open(self.src_local) as src:

                count = np.bincount(src.read(self.band).flatten())
            return np.nonzero(count != 0)[0].tolist()

        def _local_vector():

            df = gpd.read_file(self.src_local)

            return df[self.band].unique().tolist()

        # map all the function in the guess matrix (gee, type)
        unique_func = [[_local_vector, _local_image], [_ee_vector, _ee_image]]

        # get values from the selected func
        # remember to use self as a parameter
        values = unique_func[self.gee][self.input_type]()

        # create the init dictionnary
        self.src_class = {v: ("no_name", "#000000") for v in values}

        return self.src_class

    def reclassify(self):
        """
        Reclassify the input according to the provided matrix. For vector file type reclassifying correspond to add an extra column at the end, for raster the initial class band will be replaced by the new class, the oher being kept unmodified. vizualization colors will be set for both local (QGIS compatible) and assets (SEPAL vizualization compatible).

        Return:
            self
        """

        if not self.matrix:
            raise Exception(
                "You need a reclassification matrix to reclassify an asset."
            )
        if not self.band:
            raise Exception("You need to provide a band/property to reclassify.")

        @su.need_ee
        def _ee_image():

            if not self.src_gee:
                raise Exception("You need to provide source asset.")

            # create the asset description
            self.dst_gee = Path(self.folder) / f"{Path(self.src_gee).stem}_reclass"

            # load the image
            # remap according to the matrix
            from_, to_ = list(zip(*matrix.items()))

            image = ee.Image(self.src_gee)
            geometry = image.geometry() if not self.aoi_model else self.get_aoi()

            ee_image = (
                image.clip(geometry)
                .remap(from_, to_, 0, self.band)
                .select(["remapped"], [self.band])
            )

            # gather all the other band in the image
            # ee_image = ee.Image(self.src_gee).addBands(ee_image, overwrite=True)

            # add colormapping parameters
            # set return an element so we force cast it to ee.Image
            code, desc, color = zip(
                *[(str(k), str(v[0]), str(v[1])) for k, v in self.dst_class.items()]
            )

            ee_image = ee.Image(
                ee_image.set(
                    {
                        "visualization_0_name": "Classification",
                        "visualization_0_bands": self.band,
                        "visualization_0_type": "categorical",
                        "visualization_0_labels": f"no_data,{','.join(desc)}",
                        "visualization_0_palette": f"#000000,{','.join(color)}",
                        "visualization_0_values": f"0,{','.join(code)}",
                    }
                )
            )

            # save the file in a in_memeory variable
            self.dst_gee_memory = ee_image

            if self.save:
                # export
                params = {
                    "image": ee_image,
                    "assetId": str(self.dst_gee),
                    "description": self.dst_gee.stem,
                    "scale": 30,  # it should be the native resolution of the original img
                    "maxPixels": 1e13,
                    "pyramidingPolicy": {".default": "mode"},
                }

                task = ee.batch.Export.image.toAsset(**params)
                task.start()

            return self.dst_gee.stem

        @su.need_ee
        def _ee_vector():

            if not self.src_gee:
                raise Exception("You need to provide source asset.")

            # create the asset description
            self.dst_gee = Path(self.folder) / f"{Path(self.src_gee).stem}_reclass"

            # add a new propertie

            def add_prop(feat):
                """Add reclass column to the new feature"""
                index = ee_from.indexOf(feat.get(self.band))
                # if search value is not in from, -1 is returned
                new_val = ee.Algorithms.If(index.eq(-1), NO_VALUE, ee_to.get(index))
                return feat.set({"reclass": new_val})

            ee_matrix = ee.List(list(matrix.items())).unzip()
            ee_from, ee_to = ee.List(ee_matrix.get(0)), ee.List(ee_matrix.get(1))

            if self.aoi_model:
                aoi_geometry = self.get_aoi()
                self.dst_gee_memory = (
                    ee.FeatureCollection(self.src_gee)
                    .filterBounds(aoi_geometry)
                    .map(add_prop)
                )
            else:
                self.dst_gee_memory = ee.FeatureCollection(self.src_gee).map(add_prop)

            # add colormapping parameters

            if self.save:
                # export
                params = {
                    "collection": self.dst_gee_memory,
                    "assetId": str(self.dst_gee),
                    "description": str(self.dst_gee.stem),
                }

                task = ee.batch.Export.table.toAsset(**params)
                task.start()

            return self.dst_gee.stem

        def _local_image():

            if not self.src_local:
                raise Exception("You need to provide source asset.")

            # set the output file
            self.dst_local = self.dst_dir / f"{Path(self.src_local).stem}_reclass.tif"

            with rio.open(self.src_local) as src_f:

                profile = src_f.profile
                profile.update(driver="GTiff", count=1, compress="lzw", dtype=np.uint8)

                with rio.open(self.dst_local, "w", **profile) as dst_f:

                    # workon each window to avoid memory problems
                    windows = [w for _, w in src_f.block_windows()]
                    for window in windows:

                        # read the window
                        raw = src_f.read(self.band, window=window)

                        # reclassify the image based on the matrix
                        # every value that is not specified will be set to 0
                        data = np.zeros_like(raw, dtype=np.int64)

                        for old_val, new_val in matrix.items():
                            data += (raw == old_val) * new_val

                        # write it in the destination file
                        if self.save:
                            dst_f.write(data.astype(np.uint8), 1, window=window)
                    # Save raster in memory
                    self.dst_local_memory = data

                    # add the colors to the image
                    colormap = {0: (0, 0, 0)}
                    for code, item in self.dst_class.items():
                        colormap[code] = tuple(int(c * 255) for c in to_rgba(item[1]))
                    dst_f.write_colormap(self.band, colormap)

            return self.dst_local

        def _local_vector():

            if not self.src_local:
                raise Exception("You need need to provide source asset.")

            # set the output file
            self.dst_local = self.dst_dir / f"{Path(self.src_local).stem}_reclass.shp"

            # set the output file
            self.dst_local = self.dst_dir / f"{Path(self.src_local).stem}_reclass.shp"

            # read the dataset
            gdf = gpd.read_file(self.src_local)

            # map the new column
            gdf["reclass"] = gdf.apply(lambda row: matrix[row[self.band]])

            # add the colors to the gdf
            # waiting for an answer there :
            # https://gis.stackexchange.com/questions/404946/how-can-i-save-my-geopandas-symbology
            self.dst_local_memory = gdf

            if self.save:
                # save the file
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

        # tel the rest of the apps that a reclassification is finished
        self.remaped += 1
        if self.save:
            return ms.rec.rec.export[self.gee][self.input_type].format(res)

        return "Asset successfully reclassified."
