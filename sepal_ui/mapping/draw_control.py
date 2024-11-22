"""Customized drawing control."""

from copy import deepcopy
from typing import Optional

import geopandas as gpd
import ipyleaflet as ipl
from shapely import geometry as sg

from sepal_ui import color


class DrawControl(ipl.DrawControl):

    m: Optional[ipl.Map] = None
    "the map on which he drawControl is displayed. It will help control the visibility"

    def __init__(self, m: ipl.Map, **kwargs) -> None:
        """A custom DrawingControl object to handle edition of features.

        Args:
            m: the map on which he drawControl is displayed
            kwargs: any available arguments from a ipyleaflet.DrawingControl
        """
        # set some default parameters
        options = {"shapeOptions": {"color": color.info}}
        kwargs.setdefault("marker", {})
        kwargs.setdefault("circlemarker", {})
        kwargs.setdefault("polyline", {})
        kwargs.setdefault("rectangle", options)
        kwargs.setdefault("circle", options)
        kwargs.setdefault("polygon", options)

        # save the map in the member of the objects
        self.m = m

        super().__init__(**kwargs)

    def show(self) -> None:
        """Show the drawing control on the map. and clear it's content."""
        self.clear()
        self in self.m.controls or self.m.add(self)

        return

    def hide(self) -> None:
        """Hide the drawing control from the map, and clear it's content."""
        self.clear()
        self not in self.m.controls or self.m.remove(self)

        return

    def to_json(self) -> dict:
        """Return the content of the DrawControl data.

        Returned without the styling properties and using a polygonized representation of circles. The output is fully compatible with __geo_interface__.

        Returns:
            the json representation of all the geometries draw on the map
        """
        features = [self.polygonize(feat) for feat in deepcopy(self.data)]
        [feat["properties"].pop("style") for feat in features]

        return {"type": "FeatureCollection", "features": features}

    @staticmethod
    def polygonize(geo_json: dict) -> dict:
        """Transform a ipyleaflet circle (a point with a radius) into a GeoJson polygon.

        The methods preserves all the geo_json other attributes.
        If the geometry is not a circle (don't require polygonisation), do nothing.

        Params:
            geo_json: the circle geojson

        Returns:
            the polygonised feature
        """
        if "Point" not in geo_json["geometry"]["type"]:
            return geo_json

        # create shapely point
        center = sg.Point(geo_json["geometry"]["coordinates"])
        point = gpd.GeoSeries([center], crs=4326)

        radius = geo_json["properties"]["style"]["radius"]
        circle = point.to_crs(3857).buffer(radius).to_crs(4326)

        # insert it in the geo_json
        output = geo_json.copy()
        output["geometry"] = circle[0].__geo_interface__

        return output
