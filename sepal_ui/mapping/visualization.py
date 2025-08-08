"""This module provides functions to retrieve and process map visualization parameters."""

import json
import logging
import warnings
from distutils.util import strtobool
from typing import Optional

import ee

from sepal_ui import color as scolors
from sepal_ui.frontend import styles as ss
from sepal_ui.scripts.gee_interface import GEEInterface
from sepal_ui.scripts.warning import SepalWarning

log = logging.getLogger("sepalui.mapping.visualization")

PREFIX = "visualization"
"""the constant prefix for SEPAL visualization parameters"""


async def get_viz_params_async(
    gee_interface: GEEInterface,
    ee_object: ee.ComputedObject,
    vis_params: dict,
    viz_name: str,
    use_map_vis=True,
) -> tuple:
    """Asynchronously retrieve and process visualization parameters for a given Earth Engine object.

    Args:
        gee_interface: The GEE interface to use for fetching properties.
        ee_object: The Earth Engine object (Image, FeatureCollection, etc.) to process.
        vis_params: Visualization parameters to apply.
        viz_name: Name of the visualization parameters to retrieve.
        use_map_vis: Whether to use map visualization parameters.

    Returns:
        A tuple containing the processed image, object, and visualization parameters.

    Raises:
        AttributeError: If the provided Earth Engine object is not of a recognized type.
    """
    validate_ee_object(ee_object)

    props = {}

    raw_prop_list = await get_props_list_async(gee_interface, ee_object)

    viz = process_props(raw_prop_list, props)

    # get the requested vizparameters name
    # if non is set use the first one
    if viz:
        viz_name = viz_name or viz[next(iter(viz))]["name"]

    return process_vis_params(
        ee_object,
        viz=viz,
        vis_params=vis_params,
        use_map_vis=use_map_vis,
        viz_name=viz_name,
    )


def get_viz_params(
    gee_interface: GEEInterface,
    ee_object: ee.ComputedObject,
    vis_params: dict,
    viz_name: str,
    use_map_vis=True,
) -> tuple:
    """Retrieve and process visualization parameters for a given Earth Engine object.

    Args:
        gee_interface: The GEE interface to use for fetching properties.
        ee_object: The Earth Engine object (Image, FeatureCollection, etc.) to process.
        vis_params: Visualization parameters to apply.
        viz_name: Name of the visualization parameters to retrieve.
        use_map_vis: Whether to use map visualization parameters.

    Returns:
        A tuple containing the processed image, object, and visualization parameters.

    Raises:
        AttributeError: If the provided Earth Engine object is not of a recognized type.
    """
    validate_ee_object(ee_object)

    props = {}

    raw_prop_list = get_props_list(gee_interface, ee_object)

    viz = process_props(raw_prop_list, props)

    # get the requested vizparameters name
    # if non is set use the first one
    if viz:
        viz_name = viz_name or viz[next(iter(viz))]["name"]

    return process_vis_params(
        ee_object,
        viz=viz,
        vis_params=vis_params,
        use_map_vis=use_map_vis,
        viz_name=viz_name,
    )


def get_props_list(gee_interface: GEEInterface, ee_object: ee.ComputedObject) -> list:
    """Retrieve the list of visualization properties from an Earth Engine object.

    Args:
        gee_interface: The GEE interface to use for fetching properties.
        ee_object: The Earth Engine object (Image, FeatureCollection, etc.) to process.

    Returns:
        A list of visualization properties.

    Raises:
        AttributeError: If the provided Earth Engine object is not of a recognized type.
    """
    if not isinstance(ee_object, ee.Image):
        return []

    prop_names = ee_object.propertyNames()
    viz_props = prop_names.filter(ee.Filter.stringStartsWith("item", PREFIX))

    # Check if there are any visualization properties
    if gee_interface.get_info(viz_props.size()) == 0:
        log.warning("Image has no visualization properties, returning empty viz params")
        return []

    # Get only the visualization properties as a dictionary
    viz_dict = ee_object.toDictionary(viz_props)
    raw_prop_list = gee_interface.get_info(viz_dict)

    return raw_prop_list


async def get_props_list_async(gee_interface: GEEInterface, ee_object: ee.ComputedObject) -> list:
    """Asynchronously retrieve the list of visualization properties from an Earth Engine object.

    Args:
        gee_interface: The GEE interface to use for fetching properties.
        ee_object: The Earth Engine object (Image, FeatureCollection, etc.) to process.

    Returns:
        A list of visualization properties.

    Raises:
        AttributeError: If the provided Earth Engine object is not of a recognized type.
    """
    if not isinstance(ee_object, ee.Image):
        return []

    prop_names = ee_object.propertyNames()
    viz_props = prop_names.filter(ee.Filter.stringStartsWith("item", PREFIX))

    # Check if there are any visualization properties
    if await gee_interface.get_info_async(viz_props.size()) == 0:
        log.warning("Image has no visualization properties, returning empty viz params")
        return []

    # Get only the visualization properties as a dictionary
    viz_dict = ee_object.toDictionary(viz_props)
    raw_prop_list = await gee_interface.get_info_async(viz_dict)

    return raw_prop_list


def process_props(raw_prop_list: Optional[list], props: dict = {}) -> dict:
    """Process the raw visualization properties into a structured dictionary.

    Args:
        raw_prop_list: The raw list of properties retrieved from the Earth Engine object.
        props: An optional dictionary to store processed properties.

    Returns:
        A dictionary containing processed visualization properties.
    """
    if not raw_prop_list:
        return props

    # decompose each property by its number
    # and gather the properties in a sub dictionary
    for p, val in raw_prop_list.items():
        # extract the number and create the sub-dict
        _, number, name = p.split("_")
        props.setdefault(number, {})

        # modify the values according to prop key
        if isinstance(val, str):
            if name in ["bands", "palette", "labels"]:
                val = val.split(",")
            elif name in ["max", "min", "values"]:
                val = [float(i) for i in val.split(",")]
            elif name in ["inverted"]:
                val = [bool(strtobool(i)) for i in val.split(",")]

        # set the value
        props[number][name] = val

    for i in props.keys():
        if "type" in props[i]:
            # categorical values need to be cast to int
            if props[i]["type"] == "categorical":
                props[i]["values"] = [int(val) for val in props[i]["values"]]
        else:
            # if no "type" is provided guess it from the different parameters gathered
            if len(props[i]["bands"]) == 1:
                props[i]["type"] = "continuous"
            elif len(props[i]["bands"]) == 3:
                props[i]["type"] = "rgb"
            else:
                warnings.warn(
                    "the embed viz properties are incomplete or badly set, "
                    "please review our documentation",
                    SepalWarning,
                )
                props = {}

    return props


def process_vis_params(
    ee_object: ee.ComputedObject,
    viz: dict,
    vis_params: dict,
    use_map_vis: bool,
    viz_name: str = None,
) -> tuple:
    """Process the visualization parameters for a given Earth Engine object.

    Args:
        ee_object: The Earth Engine object (Image, FeatureCollection, etc.) to process.
        viz: The visualization properties dictionary.
        vis_params: The visualization parameters to apply.
        use_map_vis: Whether to use map visualization parameters.
        viz_name: Name of the visualization parameters to retrieve.

    Returns:
        A tuple containing the processed image, object, and visualization parameters.

    Raises:
        ValueError: If the provided viz_name cannot be found in the image metadata.
    """
    # apply it to vis_params
    if not vis_params and viz and use_map_vis:
        # find the viz params in the list
        try:
            vis_params = next(i for p, i in viz.items() if i["name"] == viz_name)
        except StopIteration:
            raise ValueError(
                f"the provided viz_name ({viz_name}) cannot be found in the image metadata"
            )

        # invert the bands if needed
        inverted = vis_params.pop("inverted", None)
        if inverted is not None:
            # get the index of the bands that need to be inverted
            index_list = [i for i, v in enumerate(inverted) if v is True]

            # multiply everything by -1
            for i in index_list:
                min_ = vis_params["min"][i]
                max_ = vis_params["max"][i]
                vis_params["min"][i] = max_
                vis_params["max"][i] = min_

        # specific case of categorical images
        # Pad the palette when using non-consecutive values
        # instead of remapping or using sldStyle
        # to preserve the class values in the image, for inspection
        if vis_params["type"] == "categorical":
            colors = vis_params["palette"]
            values = vis_params["values"]
            min_ = min(values)
            max_ = max(values)

            # set up a black palette of correct length
            palette = ["#000000"] * (max_ - min_ + 1)

            # replace the values within the palette
            for i, val in enumerate(values):
                palette[val - min_] = colors[i]

            # adapt the vizparams
            vis_params["palette"] = palette
            vis_params["min"] = min_
            vis_params["max"] = max_

        # specific case of hsv
        elif vis_params["type"] == "hsv":
            # set to_min to 0 and to_max to 1
            # in the original expression:
            # 'to_min + (v - from_min) * (to_max - to_min) / (from_max - from_min)'
            expression = "{band} = (b('{band}') - {from_min}) / ({from_max} - {from_min})"

            # get the maxs and mins
            # removing them from the parameter
            mins = vis_params.pop("min")
            maxs = vis_params.pop("max")

            # create the rgb bands
            asset = ee_object
            for i, band in enumerate(vis_params["bands"]):
                # adapt the expression
                exp = expression.format(from_min=mins[i], from_max=maxs[i], band=band)
                asset = asset.addBands(asset.expression(exp), [band], True)

            # set the arguments
            ee_object = asset.select(vis_params["bands"]).hsvToRgb()
            vis_params["bands"] = ["red", "green", "blue"]

    # force cast to featureCollection if needed
    if isinstance(
        ee_object,
        (
            ee.geometry.Geometry,
            ee.feature.Feature,
            ee.featurecollection.FeatureCollection,
        ),
    ):
        default_vis = json.loads((ss.JSON_DIR / "layer.json").read_text())["ee_layer"]
        default_vis.update(color=scolors.primary)

        # We want to get all the default styles and only change those whose are
        # in the provided visualization.
        default_vis.update(vis_params)

        vis_params = default_vis

        features = ee.FeatureCollection(ee_object)
        const_image = ee.Image.constant(0.5)

        try:
            image_fill = features.style(**vis_params).updateMask(const_image)
            image_outline = features.style(**vis_params)

        except AttributeError:
            # Raise a more understandable error
            raise AttributeError(
                "You can only use the following styles: 'color', 'pointSize', "
                "'pointShape', 'width', 'fillColor', 'styleProperty', "
                "'neighborhood', 'lineType'"
            )

        image = image_fill.blend(image_outline)
        obj = features

    # use directly the ee object if Image
    elif isinstance(ee_object, ee.image.Image):
        image = obj = ee_object

    # use mosaicing if the ee_object is a ImageCollection
    elif isinstance(ee_object, ee.imagecollection.ImageCollection):
        image = obj = ee_object.mosaic()

    return image, obj, vis_params


def validate_ee_object(ee_object: ee.ComputedObject) -> None:
    """Validate the type of the ee object.

    Args:
        ee_object: the ee object to validate

    Raises:
        AttributeError: if the ee_object is not an instance of ee.Image, ee.Geometry, ee.Feature or ee.FeatureCollection
    """
    # check the type of the ee object and raise an error if it's not recognized
    if not isinstance(
        ee_object,
        (
            ee.Image,
            ee.ImageCollection,
            ee.FeatureCollection,
            ee.Feature,
            ee.Geometry,
        ),
    ):
        raise AttributeError(
            "\n\nThe image argument in 'addLayer' function must be an instance of "
            "one of ee.Image, ee.Geometry, ee.Feature or ee.FeatureCollection."
        )
