import ee

from sepal_ui import sepalwidgets as sw
from sepal_ui.scripts import utils as su


class TestAssetSelect:

    default_items = [
        "OSU/GIMP/DEM",
        "ASTER/AST_L1T_003",
        "SKYSAT/GEN-A/PUBLIC/ORTHO/RGB",
    ]

    def test_init(self):

        # create an asset select that points to the folder I created for testing
        folder = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"
        std_root = "users/bornToBeAlive/sepal_ui_test"
        asset_select = sw.AssetSelect(folder=folder)

        assert isinstance(asset_select, sw.AssetSelect)
        assert f"{std_root}/france" in asset_select.items

        # create an asset select with an undefined type
        asset_select = sw.AssetSelect(folder=folder, types=["toto"])

        assert asset_select.items == []

        return

    def test_add_default(self):

        # create an asset select that points to the folder I created for testing
        folder = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"
        std_root = "users/bornToBeAlive/sepal_ui_test"
        asset_select = sw.AssetSelect(folder=folder)

        # add a partial list of asset
        asset_select.default_asset = self.default_items[1:]
        assert self.default_items[1] in asset_select.items

        # add the full list
        asset_select.default_asset = self.default_items
        assert self.default_items[0] in asset_select.items

        return

    def test_validate(self):

        # create an asset select that points to the folder I created for testing
        folder = "projects/earthengine-legacy/assets/users/bornToBeAlive/sepal_ui_test"
        std_root = "users/bornToBeAlive/sepal_ui_test"
        asset_select = sw.AssetSelect(folder=folder)

        # set a legit asset
        asset_select._validate({"new": self.default_items[0]})
        assert asset_select.valid == True

        # set a fake asset
        asset_select._validate({"new": "toto/tutu"})
        assert asset_select.error_messages != None


if __name__ == "__main__":
    unittest.main()
