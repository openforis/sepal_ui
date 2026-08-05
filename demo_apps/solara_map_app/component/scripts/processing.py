"""Earth Engine computations behind the demo layers."""

import ee
from component.model import ProcessingOutputs


def ndvi_composite() -> ee.Image:
    """Sentinel-2 NDVI over a fixed demo area, independent of the AOI."""
    polygons = ee.FeatureCollection(
        [
            ee.Feature(ee.Geometry.Rectangle([-74.15, 4.77, -74.10, 4.72]), {"name": "Tile A"}),
            ee.Feature(ee.Geometry.Rectangle([-74.09, 4.77, -74.04, 4.72]), {"name": "Tile B"}),
        ]
    )
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(polygons)
        .filterDate("2024-01-01", "2024-12-31")
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
        .median()
    )

    return s2.normalizedDifference(["B8", "B4"]).rename("NDVI")


def build_outputs(aoi_value) -> ProcessingOutputs:
    """Derive the demo Earth Engine outputs from the selected AOI."""
    fc = aoi_value.feature_collection

    # clipToCollection masks to the collection's features, so a dense AOI never
    # dissolves into one 2M-edge geometry the way clip(fc.geometry()) would
    # (issue #996). ee.Image.clip only accepts a Geometry/Feature, so a
    # FeatureCollection must go through clipToCollection.
    pixel_area = ee.Image.pixelArea().rename("pixel_area_m2").clipToCollection(fc)

    elevation = ee.Image("USGS/SRTMGL1_003").select("elevation")
    elevation_class = (
        ee.Image(1)
        .where(elevation.gte(500), 2)
        .where(elevation.gte(1500), 3)
        .updateMask(elevation.mask())
        .rename("elevation_class")
        .clipToCollection(fc)
    )

    multi_band = pixel_area.addBands(elevation_class).addBands(ee.Image.constant(1).rename("flag"))

    # Export region as the union of per-feature bounding boxes -- same trick as
    # clip, so exporting a dense AOI doesn't dissolve its geometry (issue #996).
    region = fc.map(lambda f: ee.Feature(f.geometry().bounds())).geometry().bounds()

    return ProcessingOutputs(
        pixel_area=pixel_area,
        elevation_class=elevation_class,
        multi_band=multi_band,
        region=region,
        name_prefix=aoi_value.name.replace(" ", "_"),
    )
