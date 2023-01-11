"""
All in one tile to reclassify GEE assets or local raster and create custom classifications.
"""

from pathlib import Path
from typing import Optional, Union

import ipyvuetify as v
from traitlets import link

from sepal_ui import aoi
from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms

from .reclassify_model import ReclassifyModel
from .reclassify_view import ReclassifyView
from .table_view import TableView

__all__ = ["ReclassifyTile"]


class ReclassifyTile(sw.Tile):

    result_dir: Union[Path, str] = ""
    "Directory to store the outputs (rasters, and csv_files)."

    model: Optional[ReclassifyModel] = None
    "the reclassify model to use with these inputs"

    reclassify_view: Optional[ReclassifyView] = None
    "a fully qualified ReclassifyView object"

    table_view: Optional[TableView] = None
    "a fully qualified TableView object"

    def __init__(
        self,
        results_dir: Union[Path, str] = Path.home() / "downloads",
        gee: bool = True,
        dst_class: Union[Path, str] = "",
        default_class: dict = {},
        aoi_model: Optional[aoi.AoiModel] = None,
        folder: str = "",
        **kwargs
    ) -> None:
        """
        All in one tile to reclassify GEE assets or local raster and create custom classifications.

        Args:
            results_dir: Directory to store the outputs (rasters, and csv_files). default to ~/downloads
            gee: Use GEE variant, to reclassify assets or local input. default True
            dst_class: the file to be used as destination classification. for app that require specific code system the file can be set prior and the user won't have the oportunity to change it
            default_class: the default classification system to use, need to point to existing sytem: {name: absolute_path}
            folder: the init GEE asset folder where the asset selector should start looking (debugging purpose)
        """
        # output directory
        self.results_dir = Path(results_dir)

        self.aoi_model = aoi_model
        # create the model
        self.model = ReclassifyModel(
            dst_dir=self.results_dir, gee=gee, aoi_model=self.aoi_model, folder=folder
        )

        # set the tabs elements
        self.reclassify_view = ReclassifyView(
            self.model,
            out_path=self.results_dir,
            gee=gee,
            default_class=default_class,
            aoi_model=aoi_model,
            save=True,
            folder=folder,
        ).nest_tile()

        self.table_view = TableView(out_path=self.results_dir).nest_tile()

        # create the tab
        tiles = [self.reclassify_view, self.table_view]

        self._tabs = v.Tabs(
            class_="mt-5",
            grow=True,
            # background_color='grey darken-4',
            v_model=0,
            children=[
                v.Tab(children=[t.title.children[0].children[0]], key=i)
                for i, t in enumerate(tiles)
            ],
        )

        self._content = v.TabsItems(
            v_model=0,
            children=[v.TabItem(children=[t], key=i) for i, t in enumerate(tiles)],
        )

        super().__init__(
            id_="reclassify_tile",
            title=ms.rec.tile.title,
            inputs=[self._tabs, self._content],
            **kwargs
        )

        # js interaction
        link((self._tabs, "v_model"), (self._content, "v_model"))
