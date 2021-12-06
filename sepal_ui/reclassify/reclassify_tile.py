from pathlib import Path
from traitlets import link

import ipyvuetify as v

from sepal_ui import sepalwidgets as sw
from sepal_ui.message import ms
from sepal_ui import reclassify as rec

__all__ = ["ReclassifyTile"]


class ReclassifyTile(sw.Tile):
    """

    All in one tile to reclassify GEE assets or local raster and create custom classifications

    Args:
        results_dir (str|pathlike object): Directory to store the outputs (rasters, and csv_files). default to ~/downloads
        gee (bool): Use GEE variant, to reclassify assets or local input. default True
        dst_class (str|pathlib.Path, optional): the file to be used as destination classification. for app that require specific code system the file can be set prior and the user won't have the oportunity to change it
        default_class (dict|optional): the default classification system to use, need to point to existing sytem: {name: absolute_path}
        folder(str, optional): the init GEE asset folder where the asset selector should start looking (debugging purpose)
    """

    result_dir = None
    "pathlib.Path: Directory to store the outputs (rasters, and csv_files)."

    model = None
    "ReclassifyModel: the reclassify model to use with these inputs"

    reclassify_view = None
    "ReclassifyView: a fully qualified ReclassifyView object"

    table_view = None
    "TableView: a fully qualified TableView object"

    def __init__(
        self,
        results_dir=Path.home() / "downloads",
        gee=True,
        dst_class=None,
        default_class={},
        aoi_model=None,
        folder=None,
        **kwargs
    ):

        # output directory
        self.results_dir = Path(results_dir)

        self.aoi_model = aoi_model
        # create the model
        self.model = rec.ReclassifyModel(
            dst_dir=self.results_dir, gee=gee, aoi_model=self.aoi_model, folder=folder
        )

        # set the tabs elements
        self.reclassify_view = rec.ReclassifyView(
            self.model,
            out_path=self.results_dir,
            gee=gee,
            default_class=default_class,
            aoi_model=aoi_model,
            save=True,
            folder=folder,
        ).nest_tile()

        self.table_view = rec.TableView(out_path=self.results_dir).nest_tile()

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
