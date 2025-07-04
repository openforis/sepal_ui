"""Test the GEE methods."""

import time
import warnings
from pathlib import Path

import ee
import pytest

from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms
from sepal_ui.scripts import gee


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_wait_for_completion(alert: sw.Alert, fake_task: str, gee_dir: Path, _hash: str) -> None:
    """Check we can wait for a task completion.

    Args:
        alert: an alert to display outputs
        fake_task: the name of the fake task
        gee_dir: the hashed folder where all files are saved
        _hash: the has used in file and task naming
    """
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
def test_is_task(fake_task: str) -> None:
    """Check a name is a task.

    Args:
        fake_task: the name of the running fake task
    """
    # check if it exist
    res = gee.is_task(fake_task)

    assert res is not None

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_get_assets(gee_dir: Path) -> None:
    """Check the assets are existing in the gee_dir folder and test deprecation warning.

    Args:
        gee_dir: gee_dir: the directory where gee files are exported
    """
    # get the assets from the test repository (should show deprecation warning)
    with pytest.warns(DeprecationWarning, match="Use GEEInterface.get_assets"):
        items = gee.get_assets(gee_dir)

    ee_asset_ids = [item["name"] for item in items]

    # check that they are all there
    expected_assets = [
        str(gee_dir / name)
        for name in [
            "feature_collection",
            "image",
            "subfolder",
            "subfolder/subfolder_feature_collection",
        ]
    ]

    for expected_asset in expected_assets:
        assert expected_asset in ee_asset_ids

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_is_asset(gee_dir: Path) -> None:
    """Check if the asset exist and test deprecation warnings.

    Args:
        gee_dir: gee_dir: the directory where gee files are exported
    """
    # Test with legacy parameters (should show deprecation warning)
    with pytest.warns(DeprecationWarning, match="Use GEEInterface.get_asset"):
        res = gee.is_asset(str(gee_dir / "image"), gee_dir)
        assert res is True

    with pytest.warns(DeprecationWarning, match="Use GEEInterface.get_asset"):
        res = gee.is_asset(str(gee_dir / "toto"), gee_dir)
        assert res is False

    # Test with new asset_id parameter (should still show deprecation warning)
    with pytest.warns(DeprecationWarning, match="Use GEEInterface.get_asset"):
        res = gee.is_asset(asset_id=str(gee_dir / "image"))
        assert res is True

    with pytest.warns(DeprecationWarning, match="Use GEEInterface.get_asset"):
        res = gee.is_asset(asset_id=str(gee_dir / "fake_asset"))
        assert res is False

    # Test error when no parameters provided
    with pytest.raises(ValueError, match="Either 'asset_id' or 'asset_name' must be provided"):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            gee.is_asset()

    return


@pytest.mark.skipif(not ee.data._credentials, reason="GEE is not set")
def test_is_running(fake_task: str) -> None:
    """Check if a task can be monitored.

    Args:
        fake_task: the name of the running fake task
    """
    for _ in range(30):
        time.sleep(1)
        res = gee.is_running(fake_task)
        if res is not None:
            break

    assert res is not None

    return


@pytest.fixture(scope="function")
def fake_task(gee_dir: Path, _hash: str, alert: sw.Alert) -> str:
    """Create a fake exportation task.

    Args:
        gee_dir: the directory where gee files are exported (it includes the hash in the name)
        _hash: the hash str used to run parallel test
        alert: the alert used for outputs

    Returns:
        the name of the launched task
    """
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
    gee.delete_assets(asset_id, False)

    return
