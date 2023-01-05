from pathlib import Path
from zipfile import ZipFile

import ee
import geopandas as gpd
import pytest

from sepal_ui import aoi
from sepal_ui.reclassify import ReclassifyModel, ReclassifyView


class TestReclassifyView:
    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_init_exception(alert, gee_dir):
        """Test exceptions"""

        aoi_model = aoi.AoiModel(gee=False)

        # aoi_model has to be local when using local view.
        with pytest.raises(Exception):
            ReclassifyView(aoi_model=aoi_model, gee=True, folder=gee_dir)

        return

    def test_init_local(self, view_local, class_file):

        assert view_local.model.aoi_model.gee is False
        assert view_local.gee is False

        # Check that all the classes buttons were created
        btn_paths = [btn._metadata["path"] for btn in view_local.btn_list]

        assert str(class_file) in btn_paths
        assert "custom" in btn_paths

        return

    def test_init_gee(self, view_gee):

        assert view_gee.model.aoi_model.gee is True
        assert view_gee.gee is True

        return

    def test_set_dst_class_file(self, view_local, class_file):

        # Arrange
        btn_list = [btn for btn in view_local.btn_list if btn._metadata["path"]]
        custom_btn, class_file_btn = btn_list

        # Act
        view_local._set_dst_class_file(class_file_btn, None, None)

        # Assert outlined styles
        for btn in view_local.btn_list:

            if btn._metadata["path"] == str(class_file):
                assert btn.outlined is False
            else:
                assert btn.outlined is True

        # Assert select_file visibility
        assert "d-none" in view_local.w_dst_class_file.class_

        # select custom instead
        view_local._set_dst_class_file(custom_btn, None, None)

        # check that the w_dst_class_file is now visible
        assert "d-none" not in view_local.w_dst_class_file.class_

        return

    def test_load_matrix_content(
        self,
        view_local,
        map_file_bad_char,
        map_file_bad_header,
        map_file,
        model_local_vector,
        class_file,
    ):

        # No file selected
        view_local.import_dialog.w_file.v_model = ""
        with pytest.raises(Exception):
            view_local.load_matrix_content(None, None, None)

        # Wrong characters in mapping file
        with pytest.raises(Exception):
            view_local.import_dialog.w_file.v_model = str(map_file_bad_char)
            view_local.load_matrix_content(None, None, None)

        # More than one column without headers
        with pytest.raises(Exception):
            view_local.import_dialog.w_file.v_model = str(map_file_bad_header)
            view_local.load_matrix_content(None, None, None)

        # When the table is not created before
        view_local.import_dialog.w_file.v_model = str(map_file)
        view_local.model.table_created = False
        with pytest.raises(Exception):
            view_local.load_matrix_content(None, None, None)

        # Arrange
        view_local.model = model_local_vector
        view_local.model.dst_class_file = class_file

        view_local.get_reclassify_table(None, None, None)
        view_local.load_matrix_content(None, None, None)

        return

    def test_update_band(self, view_local, model_local_vector):

        # Arrange
        table_bands = ["BoroCode", "BoroName", "Shape_Area", "Shape_Leng"]
        view_local.model = model_local_vector

        # Act
        view_local._update_band(None)

        # Assert
        assert view_local.w_code.items == table_bands

        return

    def test_reclassify(self, view_local, model_local_vector):

        view_local.model = model_local_vector
        view_local.reclassify(None, None, None)

        matrix = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}

        # Assert
        assert view_local.model.dst_local is not None

        reclassify_matrix = dict(
            zip(
                view_local.model.dst_local_memory["BoroCode"].to_list(),
                view_local.model.dst_local_memory["reclass"].to_list(),
            )
        )

        assert matrix == reclassify_matrix

        return

    @pytest.fixture
    def view_local(self, tmp_dir, class_file, alert):
        """return a local reclassify view"""

        aoi_model = aoi.AoiModel(alert, gee=False)

        return ReclassifyView(
            aoi_model=aoi_model,
            gee=False,
            out_path=tmp_dir,
            class_path=tmp_dir,
            default_class={"IPCC": str(class_file)},
        )

    @pytest.fixture
    def view_gee(self, tmp_dir, class_file, gee_dir, alert):
        """return a gee reclassify view"""

        aoi_model = aoi.AoiModel(alert, gee=True, folder=str(gee_dir))

        return ReclassifyView(
            aoi_model=aoi_model,
            gee=True,
            folder=str(gee_dir),
            out_path=tmp_dir,
            class_path=tmp_dir,
            default_class={"IPCC": str(class_file)},
        )

    @pytest.fixture(scope="class")
    def class_file(self, tmp_dir):

        file = tmp_dir / "dum_default_classes.csv"
        file.write_text(
            "1,Forest,#044D02\n"
            "2,Grassland,#F5FF00\n"
            "3,Cropland,#FF8100\n"
            "4,Wetland,#0013FF\n"
            "5,Settlement,#FFFFFF\n"
            "6,Other land,#FF00DE\n"
        )

        yield file

        file.unlink()

        return

    @pytest.fixture(scope="class")
    def map_file_bad_char(self, tmp_dir):

        bad_file = tmp_dir / "map_file_bad_char.csv"
        bad_file.write_text(",src,dst\nnot_valid,not_valid")

        yield bad_file

        bad_file.unlink()

        return

    @pytest.fixture(scope="class")
    def map_file_bad_header(self, tmp_dir):

        bad_file = tmp_dir / "map_file_bad_header.csv"
        bad_file.write_text(",xx,yy,zz\n,1,2,3")

        yield bad_file

        bad_file.unlink()

        return

    @pytest.fixture(scope="class")
    def map_file(self, tmp_dir):

        file = tmp_dir / "map_file.csv"
        file.write_text(
            ",src,dst\n0,10,1\n1,100,1\n2,11,2\n"
            "3,110,2\n4,12,3\n5,120,3\n6,130,3\n"
            "7,150,3\n8,160,3\n9,170,4\n10,180,4\n"
            "11,190,4\n12,200,4\n13,210,5\n14,30,5\n"
            "15,40,1\n16,50,1\n17,61,1\n18,90,6\n"
        )

        yield file

        file.unlink()

        return

    @pytest.fixture(scope="class")
    def model_local_vector(self, tmp_dir):

        aoi_model = aoi.AoiModel(gee=False)

        # create the vector file
        file = Path(gpd.datasets.get_path("nybb").replace("zip:", ""))

        with ZipFile(file, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        model_local = ReclassifyModel(gee=False, dst_dir=tmp_dir, aoi_model=aoi_model)

        model_local.src_local = tmp_dir / "nybb.shp"
        model_local.get_type()
        model_local.matrix = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}
        model_local.band = "BoroCode"

        yield model_local

        # delete the shp files
        [f.unlink() for f in tmp_dir.glob("nybb.*")]

        return
