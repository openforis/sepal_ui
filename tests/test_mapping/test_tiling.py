"""Preparing a raster for tile serving: COG conversion, caching and atomicity.

Everything goes through rasterio's own GDAL. The ``gdal_translate`` /
``gdaladdo`` / ``gdalwarp`` binaries cannot be a dependency -- they are not on
PyPI -- so relying on them meant a ``pip install`` silently served unprepared,
unprojected rasters.
"""

from pathlib import Path

import pytest

from pysepal.mapping.tiling import (
    _hash_for_cache,
    _predictor_for,
    _write_atomically,
    default_cache_dir,
    prepare_for_tiles,
)


def _big_raster(path: Path, dtype: str = "int16", crs: str = "EPSG:4326") -> Path:
    """A raster large enough to earn overviews."""
    import numpy as np
    import rasterio as rio
    from rasterio.transform import from_origin

    size = 1024
    data = np.ones((size, size), dtype=dtype)
    data[:, size // 2 :] = 2
    with rio.open(
        path,
        "w",
        driver="GTiff",
        height=size,
        width=size,
        count=1,
        dtype=dtype,
        crs=crs,
        transform=from_origin(0, 0, 0.001, 0.001),
    ) as ds:
        ds.write(data, 1)
    return path


def test_cache_dir_follows_the_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("PYSEPAL_TILE_CACHE", str(tmp_path / "elsewhere"))

    assert default_cache_dir() == tmp_path / "elsewhere"


def test_cache_dir_sits_on_scratch(monkeypatch, tmp_path):
    # a derived COG on SEPAL's nfs4 home export would cross the network on every
    # tile read and count against the user's quota
    import pysepal.mapping.tiling as tiling

    monkeypatch.delenv("PYSEPAL_TILE_CACHE", raising=False)
    monkeypatch.setattr(tiling, "scratch_root", lambda: tmp_path)

    assert default_cache_dir().parent == tmp_path


def test_cache_dir_is_stable_across_calls(monkeypatch, tmp_path):
    # scratch_dir() mints a new directory per call, which would mean nothing is
    # ever reused; the cache needs a fixed name under the scratch root
    import pysepal.mapping.tiling as tiling

    monkeypatch.delenv("PYSEPAL_TILE_CACHE", raising=False)
    monkeypatch.setattr(tiling, "scratch_root", lambda: tmp_path)

    assert default_cache_dir() == default_cache_dir()


def test_predictor_matches_the_sample_format():
    # predictor 2 is horizontal differencing, defined for integers only
    assert _predictor_for("int16") == 2
    assert _predictor_for("uint8") == 2
    assert _predictor_for("float32") == 3


def test_preparation_yields_a_tiled_cog_with_overviews(tmp_path: Path) -> None:
    from localtileserver.validate import validate_cog

    source = _big_raster(tmp_path / "src.tif")
    result = prepare_for_tiles(str(source), cache_dir=str(tmp_path / "cache"))

    assert validate_cog(result["path"])
    assert result["report"]["tiled"]
    assert result["report"]["overviews"][0]  # non-empty


def test_a_float_raster_converts(tmp_path: Path) -> None:
    # predictor 2 on floating point either errors or compresses badly
    from localtileserver.validate import validate_cog

    source = _big_raster(tmp_path / "float.tif", dtype="float32")
    result = prepare_for_tiles(str(source), cache_dir=str(tmp_path / "cache"))

    assert validate_cog(result["path"])
    assert result["report"]["dtype"] == "float32"


def test_prepared_raster_is_reused(byte: Path, tmp_path: Path) -> None:
    # the COG used to be rebuilt on every add_raster, so a large raster paid a
    # full conversion per call
    first = prepare_for_tiles(str(byte), cache_dir=str(tmp_path))
    stamp = Path(first["path"]).stat().st_mtime_ns

    second = prepare_for_tiles(str(byte), cache_dir=str(tmp_path))

    assert second["path"] == first["path"]
    assert Path(second["path"]).stat().st_mtime_ns == stamp


def test_resampling_choice_is_part_of_the_cache_identity(byte: Path, tmp_path: Path) -> None:
    # NEAREST and AVERAGE overviews are different pixels; sharing one entry hands
    # the second caller the first caller's resampling
    categorical = prepare_for_tiles(str(byte), cache_dir=str(tmp_path), categorical=True)
    continuous = prepare_for_tiles(str(byte), cache_dir=str(tmp_path), categorical=False)

    assert categorical["path"] != continuous["path"]


def test_a_same_size_rewrite_within_a_second_is_not_reused(tmp_path: Path) -> None:
    # whole-second mtime would call these the same raster
    import numpy as np
    import rasterio as rio
    from rasterio.transform import from_origin

    source = tmp_path / "churn.tif"
    profile = dict(
        driver="GTiff",
        height=1024,
        width=1024,
        count=1,
        dtype="int16",
        crs="EPSG:4326",
        transform=from_origin(0, 0, 0.001, 0.001),
    )
    with rio.open(source, "w", **profile) as ds:
        ds.write(np.ones((1024, 1024), dtype="int16"), 1)
    first = _hash_for_cache(str(source))

    with rio.open(source, "w", **profile) as ds:  # same byte count, same second
        ds.write(np.full((1024, 1024), 2, dtype="int16"), 1)

    assert _hash_for_cache(str(source)) != first


def test_concurrent_writers_do_not_share_a_temp_file(tmp_path: Path) -> None:
    # add_raster_async prepares in a thread pool, so a pid-only name collides
    target = tmp_path / "out.tif"
    seen = []

    with _write_atomically(target) as first:
        seen.append(first)
        with _write_atomically(target) as second:
            seen.append(second)
            Path(second).write_bytes(b"second")
        Path(first).write_bytes(b"first")

    assert seen[0] != seen[1]


def test_force_rebuilds_the_prepared_raster(byte: Path, tmp_path: Path) -> None:
    first = prepare_for_tiles(str(byte), cache_dir=str(tmp_path))
    stamp = Path(first["path"]).stat().st_mtime_ns

    second = prepare_for_tiles(str(byte), cache_dir=str(tmp_path), force=True)

    assert second["path"] == first["path"]
    assert Path(second["path"]).stat().st_mtime_ns != stamp


def test_warping_reprojects_to_web_mercator(byte: Path, tmp_path: Path) -> None:
    # sbae-design serves its uploads warped, so tiles are cut in the CRS they
    # are served in instead of being reprojected per request
    plain = prepare_for_tiles(str(byte), cache_dir=str(tmp_path))
    warped = prepare_for_tiles(str(byte), cache_dir=str(tmp_path), warp_to_3857=True)

    assert plain["report"]["epsg"] != 3857  # byte.tif is UTM
    assert warped["report"]["epsg"] == 3857
    assert warped["path"] != plain["path"]  # the two live side by side in the cache


def test_warping_writes_no_intermediate(byte: Path, tmp_path: Path) -> None:
    # the WarpedVRT reprojects lazily, so the COG copy is the only write
    prepare_for_tiles(str(byte), cache_dir=str(tmp_path), warp_to_3857=True)

    assert not list(tmp_path.glob("*.warp.tif"))
    assert not list(tmp_path.glob("*.part"))


def test_warping_survives_a_pruned_gdal_env(byte: Path, tmp_path: Path, monkeypatch) -> None:
    # prune_foreign_gdal_env strips these; in-process GDAL finds its own data,
    # which a subprocess resolved from another prefix could not
    for var in ("PROJ_DATA", "PROJ_LIB", "GDAL_DATA"):
        monkeypatch.delenv(var, raising=False)

    result = prepare_for_tiles(str(byte), cache_dir=str(tmp_path), warp_to_3857=True)

    assert result["report"]["epsg"] == 3857


def test_an_already_good_raster_is_served_untouched(tmp_path: Path) -> None:
    source = _big_raster(tmp_path / "src.tif")
    prepared = prepare_for_tiles(str(source), cache_dir=str(tmp_path / "cache"))["path"]

    # feeding the prepared COG back in has nothing left to do
    again = prepare_for_tiles(prepared, cache_dir=str(tmp_path / "cache"))

    assert again["path"] == prepared


def test_a_failed_write_leaves_no_half_built_file(tmp_path: Path) -> None:
    # a reader that opens a partial GeoTIFF fails as if the source were corrupt
    target = tmp_path / "out.tif"

    with pytest.raises(RuntimeError):
        with _write_atomically(target) as tmp:
            Path(tmp).write_bytes(b"half a raster")
            raise RuntimeError("conversion exploded")

    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_an_atomic_write_lands_on_the_target(tmp_path: Path) -> None:
    target = tmp_path / "out.tif"

    with _write_atomically(target) as tmp:
        Path(tmp).write_bytes(b"a whole raster")

    assert target.read_bytes() == b"a whole raster"


def test_optimize_for_tiles_serves_the_raw_raster_on_failure(monkeypatch):
    # best-effort: a broken optimization must not stop the raster from tiling
    import pysepal.mapping.tiling as tiling

    def _boom(*args, **kwargs):
        raise RuntimeError("conversion exploded")

    monkeypatch.setattr(tiling, "prepare_for_tiles", _boom)

    assert tiling._optimize_for_tiles("/data/raster.tif") == "/data/raster.tif"
