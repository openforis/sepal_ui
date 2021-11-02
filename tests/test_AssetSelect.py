import ee
import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su


class TestAssetSelect:
    def test_init(self, gee_dir):

        # create an asset select that points to the folder I created for testing
        asset_select = sw.AssetSelect(folder=gee_dir)

        assert isinstance(asset_select, sw.AssetSelect)
        assert "users/bornToBeAlive/sepal_ui_test/france" in asset_select.items

        # create an asset select with an undefined type
        asset_select = sw.AssetSelect(folder=gee_dir, types=["toto"])

        assert asset_select.items == []

        return

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

    def test_validate(self, asset_select, default_items):

        # set a legit asset
        asset_select._validate({"new": default_items[0]})
        assert asset_select.valid == True
        assert asset_select.error_messages is None
        assert asset_select.error == False

        # set a fake asset
        asset_select._validate({"new": "toto/tutu"})
        assert asset_select.error_messages is not None
        assert asset_select.valid == False
        assert asset_select.error == True

        # set a real asset but with wrong type
        asset_select.types = ["TABLE"]
        asset_select._validate({"new": default_items[0]})
        assert asset_select.error_messages is not None
        assert asset_select.valid == False
        assert asset_select.error == True

        return

    def test_check_types(self, asset_select, asset_france):

        # remove the project from asset name
        asset_france = asset_france.replace("projects/earthengine-legacy/assets/", "")

        # check that the list of asset is complete
        assert asset_france in asset_select.items

        # set an IMAGE type
        asset_select.types = ["IMAGE"]
        assert asset_france not in asset_select.items

        # set a type list with a non legit asset type
        asset_select.types = ["IMAGE", "toto"]
        assert asset_select.types == ["IMAGE"]

        return

    @pytest.fixture
    def default_items(self):
        """some default public data from GEE"""

        return [
            "OSU/GIMP/DEM",
            "ASTER/AST_L1T_003",
            "SKYSAT/GEN-A/PUBLIC/ORTHO/RGB",
        ]

    @pytest.fixture
    def asset_select(self, gee_dir):
        """create a default assetSelect"""

        return sw.AssetSelect(folder=gee_dir)
