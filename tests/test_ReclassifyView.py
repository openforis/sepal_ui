import pytest
from pathlib import Path
from sepal_ui.reclassify import ReclassifyView, ReclassifyModel


@pytest.fixture
def dum_dir(dum_dir):
    """Creates a dummy directory"""

    new_dir = dum_dir / "reclassify/"
    new_dir.mkdir(exist_ok=True, parents=True)

    return new_dir


@pytest.fixture
def model_local_vector(dum_dir, aoi_model_local):

    model_local = ReclassifyModel(
        gee=False, dst_dir=dum_dir, aoi_model=aoi_model_local, save=True
    )

    # Input type=False to vector, True to Image
    model_local.src_local = aoi_model_local.default_vector
    model_local.input_type = False
    model_local.matrix = {1: 6, 2: 7, 3: 8, 4: 9, 5: 10}
    model_local.band = "BoroCode"

    return model_local


@pytest.fixture
def class_file(dum_dir):

    file = dum_dir / "dum_default_classes.csv"
    file.write_text(
        "1,Forest,#044D02\n"
        "2,Grassland,#F5FF00\n"
        "3,Cropland,#FF8100\n"
        "4,Wetland,#0013FF\n"
        "5,Settlement,#FFFFFF\n"
        "6,Other land,#FF00DE\n"
    )

    return file


@pytest.fixture
def map_file(dum_dir):

    file = dum_dir / "mapping_file.csv"
    file.write_text(
        ",src,dst\n0,10,1\n1,100,1\n2,11,2\n"
        "3,110,2\n4,12,3\n5,120,3\n6,130,3\n"
        "7,150,3\n8,160,3\n9,170,4\n10,180,4\n"
        "11,190,4\n12,200,4\n13,210,5\n14,30,5\n"
        "15,40,1\n16,50,1\n17,61,1\n18,90,6\n"
    )

    return file


@pytest.fixture
def view_local(aoi_model_local, class_file):

    return ReclassifyView(
        gee=False,
        aoi_model=aoi_model_local,
        default_class={
            "IPCC": str(class_file),
        },
    )


@pytest.fixture
def view_gee(aoi_model_gee, class_file):

    return ReclassifyView(
        gee=True,
        aoi_model=aoi_model_gee,
        default_class={
            "IPCC": str(class_file),
        },
    )


def test_init_exception(aoi_model_local):
    """Test exceptions"""

    # aoi_model has to be local when using local view.
    with pytest.raises(Exception):
        reclassify_view = ReclassifyView(aoi_model=aoi_model_local, gee=True)


def test_init_local(view_local, class_file):

    assert view_local.model.aoi_model.ee is False
    assert view_local.gee is False

    # Check that all the classes buttons were created
    btn_paths = [btn._metadata["path"] for btn in view_local.btn_list]

    assert str(class_file) in btn_paths
    assert "custom" in btn_paths


def test_init_gee(view_gee):

    assert view_gee.model.aoi_model.ee is True
    assert view_gee.gee is True


def test_set_dst_class_file(view_local, class_file):

    # Arrage
    (
        custom_btn,
        class_file_btn,
    ) = [btn for btn in view_local.btn_list if btn._metadata["path"]]

    # Act
    view_local._set_dst_class_file(class_file_btn, None, None)
    print("class_file_btn", class_file_btn._metadata)
    # Assert outlined styles
    for btn in view_local.btn_list:

        if btn._metadata["path"] == str(class_file):
            assert btn.outlined is False
        else:
            assert btn.outlined is True

    # Assert select_file visibility
    assert "d-none" in view_local.w_dst_class_file.class_

    view_local._set_dst_class_file(custom_btn, None, None)

    assert "d-none" not in view_local.w_dst_class_file.class_


def test_load_matrix_content(
    view_local, map_file, dum_dir, class_file, model_local_vector
):

    # No file selected
    view_local.import_dialog.w_file.v_model = ""
    with pytest.raises(Exception):
        view_local.load_matrix_content(None, None, None)

    # Wrong characters in mapping file
    with pytest.raises(Exception):
        bad_file = dum_dir / "bad_mapping_file.csv"
        bad_file.write_text(",src,dst\nnot_valid,not_valid")
        view_local.import_dialog.w_file.v_model = str(bad_file)
        view_local.load_matrix_content(None, None, None)

    # More than one column without headers
    with pytest.raises(Exception):
        bad_file = dum_dir / "bad_mapping_file.csv"
        bad_file.write_text(",xx,yy,zz\n,1,2,3")
        view_local.import_dialog.w_file.v_model = str(bad_file)
        view_local.load_matrix_content(None, None, None)

    # When the table is not created before
    view_local.import_dialog.w_file.v_model = map_file
    view_local.model.table_created = False
    with pytest.raises(Exception):
        view_local.load_matrix_content(None, None, None)

    # Arrange
    view_local.model = model_local_vector
    view_local.model.dst_class_file = class_file

    view_local.get_reclassify_table(None, None, None)
    view_local.load_matrix_content(None, None, None)


def test_update_band(view_local, model_local_vector):

    # Arrange

    table_bands = ["BoroCode", "BoroName", "Shape_Area", "Shape_Leng"]
    view_local.model = model_local_vector

    # Act
    view_local._update_band(None)

    # Assert
    assert view_local.w_code.items == table_bands


def test_reclassify(view_local, model_local_vector):

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
