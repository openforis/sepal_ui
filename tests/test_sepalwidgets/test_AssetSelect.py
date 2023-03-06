from pathlib import Path

import ee
import pytest

from sepal_ui import sepalwidgets as sw


class TestAssetSelect:
    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_init(self, gee_dir, gee_user_dir):

        # create an asset select that points to the folder I created for testing
        asset_select = sw.AssetSelect(folder=str(gee_dir))
        assert isinstance(asset_select, sw.AssetSelect)
        assert str(gee_user_dir / "image") in asset_select.items

        # create an asset select with an undefined type
        asset_select = sw.AssetSelect(folder=str(gee_dir), types=["toto"])
        assert asset_select.items == []

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_add_default(self, asset_select, default_items):

        # add a partial list of asset
        asset_select.default_asset = default_items[1:]
        assert default_items[1] in asset_select.items

        # add the full list
        asset_select.default_asset = default_items
        assert default_items[0] in asset_select.items

        # add one item as a string
        asset_select.default_asset = default_items[0]
        assert default_items[0] in asset_select.items

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_validate(self, asset_select, default_items):

        # set a legit asset
        asset_select._validate({"new": default_items[0]})
        assert asset_select.valid is True
        assert asset_select.error_messages is None
        assert asset_select.error is False

        # set a fake asset
        asset_select._validate({"new": "toto/tutu"})
        assert asset_select.error_messages is not None
        assert asset_select.valid is False
        assert asset_select.error is True

        # set a real asset but with wrong type
        asset_select.types = ["TABLE"]
        asset_select._validate({"new": default_items[0]})
        assert asset_select.error_messages is not None
        assert asset_select.valid is False
        assert asset_select.error is True

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_check_types(self, asset_select, gee_user_dir):

        # check that the list of asset is complete
        assert str(gee_user_dir / "image") in asset_select.items
        assert str(gee_user_dir / "feature_collection") in asset_select.items
        assert (
            str(gee_user_dir / "subfolder/subfolder_feature_collection")
            in asset_select.items
        )

        # set an IMAGE type
        asset_select.types = ["IMAGE"]
        assert str(gee_user_dir / "image") in asset_select.items
        assert str(gee_user_dir / "feature_collection") not in asset_select.items
        assert (
            str(gee_user_dir / "subfolder/subfolder_feature_collection")
            not in asset_select.items
        )

        # set a type list with a non legit asset type
        asset_select.types = ["IMAGE", "toto"]
        assert asset_select.types == ["IMAGE"]

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_get_items(self, asset_select, gee_user_dir):

        # test function itself
        asset_select.items = []
        asset_select._get_items()

        assert str(gee_user_dir / "image") in asset_select.items

        # Test button event
        # we shoud export an extra asset and check if the new one is here but
        # that is 30 extra seconds so we cannot afford yet
        asset_select.items = []
        asset_select.fire_event("click:prepend", None)

        assert str(gee_user_dir / "image") in asset_select.items

    @pytest.fixture
    def default_items(self):
        """some default public data from GEE."""
        return [
            "OSU/GIMP/DEM",
            "ASTER/AST_L1T_003",
            "SKYSAT/GEN-A/PUBLIC/ORTHO/RGB",
        ]

    @pytest.fixture
    def asset_select(self, gee_dir):
        """create a default assetSelect."""
        return sw.AssetSelect(folder=str(gee_dir))

    @pytest.fixture(scope="class")
    def gee_user_dir(self, gee_dir):
        """return the path to the gee_dir assets without the project elements."""
        legacy_project = Path("projects/earthengine-legacy/assets")

        return gee_dir.relative_to(legacy_project)
