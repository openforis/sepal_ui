import time

import ee
import pytest

from sepal_ui.message import ms
from sepal_ui.scripts import gee


class TestGee:
    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_wait_for_completion(self, alert, fake_task, gee_dir, _hash):

        # wait for the end of the the fake task
        res = gee.wait_for_completion(fake_task, alert)

        assert res == "COMPLETED"
        assert alert.type == "success"
        assert alert.children[1].children[0] == ms.status.format("COMPLETED")

        # check that an error is raised when trying to overwrite a existing asset
        description = "feature_collection"
        point = ee.FeatureCollection(ee.Geometry.Point([1.5, 1.5]))
        task_config = {
            "collection": point,
            "description": f"{description}_{_hash}",
            "assetId": str(gee_dir / description),
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()

        with pytest.raises(Exception):
            res = gee.wait_for_completion(description, alert)

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_is_task(self, fake_task):

        # check if it exist
        res = gee.is_task(fake_task)

        assert res is not None

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_get_assets(self, gee_dir):

        # get the assets from the test repository
        list_ = gee.get_assets(str(gee_dir))

        # check that they are all there
        names = [
            "feature_collection",
            "image",
            "subfolder",
            "subfolder/subfolder_feature_collection",
        ]

        for item, name in zip(list_, names):
            assert item["name"] == str(gee_dir / name)

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_isAsset(self, gee_dir):

        # real asset
        res = gee.is_asset(str(gee_dir / "image"), str(gee_dir))
        assert res is True

        # fake asset
        res = gee.is_asset(str(gee_dir / "toto"), str(gee_dir))
        assert res is False

        return

    @pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
    def test_is_running(self, fake_task):

        for _ in range(30):
            time.sleep(1)
            res = gee.is_running(fake_task)
            if res is not None:
                break

        assert res is not None

        return

    @pytest.fixture
    def fake_task(self, gee_dir, _hash, alert):
        """create a fake exportation task"""

        # init an asset
        point = ee.FeatureCollection(ee.Geometry.Point([1.5, 1.5]))
        name = f"fake_collection_{_hash}"
        asset_id = str(gee_dir / name)

        # launch the task
        task_config = {
            "collection": point,
            "description": name,
            "assetId": asset_id,
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()

        yield name

        # delete the task asset
        gee.wait_for_completion(name, alert)
        ee.data.deleteAsset(asset_id)

        return
