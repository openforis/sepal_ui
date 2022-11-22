import os
import time

import ee
import pytest
from sepal_ui.message import ms
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su

su.init_ee()


@pytest.mark.skipif(
    "EE_DECRYPT_KEY" in os.environ, reason="Don't work with Gservice account"
)
class TestGee:
    def test_wait_for_completion(
        self, alert, fake_task, asset_description, asset_france
    ):

        res = gee.wait_for_completion(asset_description, alert)

        assert res == "COMPLETED"
        assert alert.type == "success"
        assert alert.children[1].children[0] == ms.status.format("COMPLETED")

        # check that an error is raised when trying to overwrite a existing asset
        description = "france"
        point = ee.FeatureCollection(ee.Geometry.Point([1.5, 1.5]))
        task_config = {
            "collection": point,
            "description": description,
            "assetId": asset_france,
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()

        with pytest.raises(Exception):
            res = gee.wait_for_completion(description, alert)

        return

    def test_is_task(self, fake_task, asset_description):

        # check if it exist
        res = gee.is_task(asset_description)

        assert res is not None

        return

    def test_get_assets(self, gee_dir):

        # get the assets from the test repository
        list_ = gee.get_assets(gee_dir)

        # check that they are all there
        names = ["corsica_template", "folder", "france", "imageViZExample", "italy"]

        for item, name in zip(list_, names):
            assert item["name"] == f"{gee_dir}/{name}"

        return

    def test_isAsset(self, gee_dir, asset_france):

        # real asset
        res = gee.is_asset(asset_france, gee_dir)
        assert res is True

        # fake asset
        res = gee.is_asset(f"{gee_dir}/toto", gee_dir)
        assert res is False

        return

    def test_is_running(self, fake_task, asset_description):

        for _ in range(30):
            time.sleep(1)
            res = gee.is_running(asset_description)
            if res is not None:
                break

        assert res is not None

        return

    @pytest.fixture
    def fake_task(self, asset_id, asset_description, alert):

        # create a fake exportation task
        point = ee.FeatureCollection(ee.Geometry.Point([1.5, 1.5]))
        task_config = {
            "collection": point,
            "description": asset_description,
            "assetId": asset_id,
        }
        task = ee.batch.Export.table.toAsset(**task_config)
        task.start()

        yield task

        # delete the task asset
        gee.wait_for_completion(asset_description, alert)
        ee.data.deleteAsset(asset_id)

        return
