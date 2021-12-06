from pathlib import Path
from traitlets import Unicode

import ipyvuetify as v
import pandas as pd

from .parameters import NO_VALUE, MATRIX_NAMES
import sepal_ui.sepalwidgets as sw
from sepal_ui.scripts import utils as su
from sepal_ui.message import ms
from sepal_ui.scripts.utils import loading_button
from .reclassify_model import ReclassifyModel

__all__ = ["ReclassifyView"]


class ImportMatrixDialog(v.Dialog):
    """
    Dialog to select the file to use and fill the matrix

    Args:
        folder (pathlike object): the path to the saved classifications

    Attributes:
        file (str): the file to use
    """

    file = Unicode("").tag(sync=True)

    def __init__(self, folder, **kwargs):

        # create the 3 widgets
        title = v.CardTitle(children=["Load reclassification matrix"])
        self.w_file = sw.FileInput(label="filename", folder=folder)
        self.load_btn = sw.Btn("Load")
        cancel = sw.Btn("Cancel", outlined=True)
        actions = v.CardActions(children=[cancel, self.load_btn])

        # default params
        self.value = False
        self.max_width = 500
        self.overlay_opacity = 0.7
        self.persistent = True
        self.children = [v.Card(class_="pa-4", children=[title, self.w_file, actions])]

        # create the dialog
        super().__init__(**kwargs)

        # js behaviour
        cancel.on_event("click", self._cancel)

    def _cancel(self, widget, event, data):
        """exit and do nothing"""

        self.value = False

        return self

    def show(self):

        self.value = True

        return self


class SaveMatrixDialog(v.Dialog):
    """
    Dialog to setup the name of the output matrix file

    Args:
        folder (pathlike object): the path to the save folder. default to ~/
    """

    def __init__(self, folder=Path.home(), **kwargs):

        # save the matrix
        self._matrix = {}
        self.folder = Path(folder)

        # create the widgets
        title = v.CardTitle(children=["Save matrix"])
        self.w_file = v.TextField(label="filename", v_model=None)
        btn = sw.Btn("Save matrix")
        cancel = sw.Btn("Cancel", outlined=True)
        actions = v.CardActions(children=[cancel, btn])
        self.alert = sw.Alert(children=["Choose a name for the output"]).show()

        # default parameters
        self.value = False
        self.max_width = 500
        self.overlay_opcity = 0.7
        self.persistent = True
        self.children = [
            v.Card(class_="pa-4", children=[title, self.w_file, self.alert, actions])
        ]

        # create the dialog
        super().__init__(**kwargs)

        # js behaviour
        cancel.on_event("click", self._cancel)
        btn.on_event("click", self._save)
        self.w_file.on_event("blur", self._sanitize)
        self.w_file.observe(self._store_info, "v_model")

    def _store_info(self, change):
        """Display where will be the file written"""

        new_val = change["new"]

        out_file = self.folder / f"{su.normalize_str(new_val)}.csv"
        msg = f"Your file will be saved as: {out_file}"

        if not new_val:
            msg = "Choose a name for the output"

        self.alert.add_msg(msg)

    def _cancel(self, widget, event, data):
        """do nothing and exit"""

        self.w_file.v_model = None
        self.value = False

        return self

    def _save(self, widget, event, data):
        """save the matrix in a specified file"""

        file = self.folder / f"{su.normalize_str(self.w_file.v_model)}.csv"

        matrix = pd.DataFrame.from_dict(self._matrix, orient="index").reset_index()
        matrix.columns = MATRIX_NAMES
        matrix.to_csv(file, index=False)

        # hide the dialog
        self.value = False

        return self

    def show(self, matrix):
        """show the dialog and set the matrix values"""

        self._matrix = matrix

        # Reset file name
        self.w_file.v_model = ""

        self.value = True

        return self

    def _sanitize(self, widget, event, data):
        """sanitize the used name when saving"""

        if not self.w_file.v_model:
            return self

        self.w_file.v_model = su.normalize_str(self.w_file.v_model)

        return self


class ClassSelect(sw.Select):
    """
    Custom widget to pick the value of a original class in the new classification system

    Args:
        new_codes(dict): the dict of the new codes to use as items {code: (name, color)}
        code (int): the orginal code of the class
    """

    def __init__(self, new_codes, old_code, **kwargs):

        # set default parameters
        self.items = [
            {"text": f"{code}: {item[0]}", "value": code}
            for code, item in new_codes.items()
        ]
        self.dense = True
        self.multiple = False
        self.chips = True
        self._metadata = {"class": old_code}
        self.v_model = None
        self.clearable = True

        # init the select
        super().__init__(**kwargs)


class ReclassifyTable(sw.SimpleTable):
    """
    Table to store the reclassifying information.
    2 columns are integrated, the new class value and the values in the original input
    One can select multiple class to be reclassify in the new classification

    Args:
        model (ReclassifyModel): model embeding the traitlet dict to store the reclassifying matrix. keys: class value in dst, values: list of values in src.
        dst_classes (dict|optional): a dictionnary that represent the classes of new the new classification table as {class_code: (class_name, class_color)}. class_code must be ints and class_name str.
        src_classes (dict|optional): the list of existing values within the input file {class_code: (class_name, class_color)}

    Attributes:
        HEADER (list): name of the column header (from, to)
        model (ReclassifyModel): the reclassifyModel object to manipulate the
            input file and save parameters
    """

    HEADERS = ms.rec.rec.headers

    def __init__(self, model, dst_classes={}, src_classes={}, **kwargs):

        # default parameters
        self.dense = True

        # create the table
        super().__init__(**kwargs)

        # save the model
        self.model = model

        # create the table elements
        self._header = [
            v.Html(
                tag="tr",
                children=[v.Html(tag="th", children=[h]) for h in self.HEADERS],
            )
        ]
        self.set_table(dst_classes, src_classes)

    def set_table(self, dst_classes, src_classes):
        """
        Rebuild the table content based on the new_classes and codes provided

        Args:
            dst_classes (dict|optional): a dictionnary that represent the classes of new the new classification table as {class_code: (class_name, class_color)}. class_code must be ints and class_name str.
            src_classes (dict|optional): the list of existing values within the input file {class_code: (class_name, class_color)}

        Return:
            self
        """

        # reset the matrix
        self.model.matrix = {code: 0 for code in src_classes.keys()}

        # create the select list
        # they need to observe each other to adapt the available class list dynamically
        self.class_select_list = {
            k: ClassSelect(dst_classes, k) for k in src_classes.keys()
        }

        rows = [
            v.Html(
                tag="tr",
                children=[
                    v.Html(tag="td", children=[f"{code}: {item[0]}"]),
                    v.Html(tag="td", children=[self.class_select_list[code]]),
                ],
            )
            for code, item in src_classes.items()
        ]

        # add an empty row at the end to make the table more visible when it's empty
        rows += [
            v.Html(
                tag="tr",
                children=[
                    v.Html(tag="td", children=[""]),
                    v.Html(
                        tag="td",
                        children=["" if len(dst_classes) else "No data available"],
                    ),
                ],
            )
        ]

        self.children = [v.Html(tag="tbody", children=self._header + rows)]

        # js behaviour
        [
            w.observe(self._update_matrix_values, "v_model")
            for w in self.class_select_list.values()
        ]

        return self

    def _update_matrix_values(self, change):
        """Update the appropriate matrix value when a Combo select change"""

        # get the code of the class in the src classification
        code = change["owner"]._metadata["class"]

        # bind it to classes in the dst classification
        self.model.matrix[code] = change["new"] if change["new"] else 0

        return self


class ReclassifyView(sw.Card):
    """
    Stand-alone Card object allowing the user to reclassify a input file. the input can be of any type (vector or raster) and from any source (local or GEE).
    The user need to provide a destination classification file (table) in the following format : 3 headless columns: 'code', 'desc', 'color'. Once all the old class have been attributed to their new class the file can be exported in the source format to local memory or GEE. the output is also savec in memory for further use in the app. It can be used as a tile in a sepal_ui app. The id_ of the tile is set to "reclassify_tile"

    Args:
        model (ReclassifyModel): the reclassify model to manipulate the
            classification dataset. default to a new one
        class_path (str,optional): Folder path containing already existing
            classes. Default to ~/
        out_path (str,optional): the folder to save the created classifications.
            default to ~/downloads
        gee (bool): either or not to set :code:`gee` to True. default to False
        dst_class (str|pathlib.Path, optional): the file to be used as destination classification. for app that require specific code system the file can be set prior and the user won't have the oportunity to change it
        default_class (dict|optional): the default classification system to use, need to point to existing sytem: {name: absolute_path}
        folder(str, optional): the init GEE asset folder where the asset selector should start looking (debugging purpose)
        save (bool, optional): Whether to write/export the result or not.
        enforce_aoi (bool, optional): either or not an aoi should be set to allow the reclassification
    """

    MAX_CLASS = 20
    "int: the number of line in the table to trigger the display of an extra toolbar and alert"

    model = None
    "ReclassifyModel: the reclassify model to manipulate the classification dataset"

    gee = None
    "bool: either being linked to gee or not (use local file or GEE asset for the rest of the app)"

    alert = None
    "sw.Alert: the alert to display informations about computation"

    title = None
    "v.Cardtitle: the title of the card"

    w_asset = None
    "sw.AssetSelect: the widget to select an asset input"

    w_raster = None
    "sw.FileInput: the widget to select a file input"

    w_image = None
    "Widget: wraper of the input. linked to w_asset if gee=True, else to w_raster"

    w_code = None
    "int|str: widget to select the band/property used as init classification in the input file"

    get_table_btn = None
    "sw.Btn: the btn to load the data in the reclassification table"

    w_dst_class_file = None
    "sw.FileInput: widget to select the new classification system file (3 headless columns: 'code', 'desc', 'color')"

    reclassify_table = None
    "ReclassifyTable: the reclassification table populated via the previous widgets"

    reclassify_btn = None
    "sw.Btn: the btn to launch the reclassifying process"

    def __init__(
        self,
        model=None,
        class_path=Path.home(),
        out_path=Path.home() / "downloads",
        gee=False,
        dst_class=None,
        default_class={},
        aoi_model=None,
        save=True,
        folder=None,
        enforce_aoi=False,
        **kwargs,
    ):

        # create metadata to make it compatible with the framwork app system
        self._metadata = {"mount_id": "reclassify_tile"}

        # init card parameters
        self.class_ = "pa-5"

        # create the object
        super().__init__(**kwargs)

        # set up a default model
        self.model = model or ReclassifyModel(
            gee=gee,
            dst_dir=out_path,
            aoi_model=aoi_model,
            folder=folder,
            save=save,
            enforce_aoi=enforce_aoi,
        )

        if enforce_aoi != self.model.enforce_aoi:
            raise Exception(
                "Both reclassify_model.gee and reclassify_view parameters has to be equals."
                + f"Received {enforce_aoi} for reclassify_view and {self.model.enforce_aoi} for reclassify_model."
            )

        # set the folders
        self.class_path = Path(class_path)
        self.out_path = Path(out_path)

        # save the gee binding
        self.gee = gee
        if gee:
            su.init_ee()

        # create an alert to display information to the user
        self.alert = sw.Alert()

        # set the title of the card
        self.title = v.CardTitle(
            children=[v.Html(tag="h2", children=[ms.rec.rec.title])]
        )

        # create the input widgets
        self.w_input_title = v.Html(
            tag="h2", children=[ms.rec.rec.input.title], class_="mt-5"
        )

        if self.gee:
            self.w_image = sw.AssetSelect(label=ms.rec.rec.input.asset, folder=folder)
        else:
            self.w_image = sw.FileInput(
                [".tif", ".vrt", ".tiff", ".geojson", ".shp"],
                label=ms.rec.rec.input.file,
            )

        self.w_code = v.Select(
            label=ms.rec.rec.input.band.label,
            hint=ms.rec.rec.input.band.hint,
            v_model=None,
            items=[],
            persistent_hint=True,
        )

        w_optional_title = v.Html(tag="h3", children=[ms.rec.rec.input.optional])
        self.w_src_class_file = sw.FileInput(
            [".csv"], label=ms.rec.rec.input.classif.label, folder=self.class_path
        )
        self.w_optional = v.ExpansionPanels(
            class_="mt-5",
            children=[
                v.ExpansionPanel(
                    children=[
                        v.ExpansionPanelHeader(children=[w_optional_title]),
                        v.ExpansionPanelContent(children=[self.w_src_class_file]),
                    ]
                )
            ],
        )

        # create the destination class widgetss
        self.w_class_title = v.Html(
            tag="h2", children=[ms.rec.rec.input.classif.title], class_="mt-5"
        )

        if not dst_class:
            self.w_dst_class_file = sw.FileInput(
                [".csv"], label=ms.rec.rec.input.classif.label, folder=self.class_path
            ).hide()
        else:
            # We could save a little of time without creating this
            self.w_dst_class_file.select_file(dst_class).hide()

        self.btn_list = [
            sw.Btn(
                "Custom",
                _metadata={"path": "custom"},
                small=True,
                class_="mr-2",
                outlined=True,
            )
        ] + [
            sw.Btn(
                f"use {name}",
                _metadata={"path": path},
                small=True,
                class_="mr-2",
                outlined=True,
            )
            for name, path in default_class.items()
        ]
        self.w_default = v.Flex(class_="mt-5", children=self.btn_list)

        # set the table and its toolbar
        self.w_table_title = v.Html(
            tag="h2", children=[ms.rec.rec.table], class_="mt-5"
        )

        self.save_dialog = SaveMatrixDialog(folder=out_path)
        self.import_dialog = ImportMatrixDialog(folder=out_path)
        self.get_table = sw.Btn(
            ms.rec.rec.input.btn, "mdi-table", color="success", small=True
        )
        self.import_table = sw.Btn(
            "import", "mdi-download", color="secondary", small=True, class_="ml-2 mr-2"
        )
        self.save_table = sw.Btn(
            "save", "mdi-content-save", color="secondary", small=True
        )
        self.reclassify_btn = sw.Btn(
            ms.rec.rec.btn, "mdi-checkerboard", small=True, disabled=True
        )

        self.toolbar = v.Toolbar(
            class_="d-flex mb-6",
            flat=True,
            children=[
                self.save_dialog,
                self.import_dialog,
                v.ToolbarTitle(children=["Actions"]),
                v.Divider(class_="mx-4", inset=True, vertical=True),
                self.get_table,
                v.Divider(class_="mx-4", inset=True, vertical=True),
                v.Flex(class_="ml-auto", children=[self.import_table, self.save_table]),
                v.Divider(class_="mx-4", inset=True, vertical=True),
                self.reclassify_btn,
            ],
        )

        self.reclassify_table = ReclassifyTable(self.model)

        # create a duplicate layout that include the alert and the different btns
        # it will be displayed if the number of class > MAX_CLASS
        self.duplicate_layout = v.Layout(
            class_="d-none", children=[self.toolbar, self.alert]
        )

        # bind to the model
        # bind to the 2 raster and asset as they cannot be displayed at the same time
        self.model = (
            self.model.bind(self.w_image, "src_gee" if self.gee else "src_local")
            .bind(self.w_code, "band")
            .bind(self.w_dst_class_file, "dst_class_file")
        )

        # create the layout
        self.children = [
            self.title,
            self.w_input_title,
            self.w_image,
            self.w_code,
            self.w_optional,
            self.w_class_title,
            self.w_default,
            self.w_dst_class_file,
            self.alert,
            self.w_table_title,
            self.toolbar,
            self.reclassify_table,
            self.duplicate_layout,
        ]

        # Decorate functions
        self.reclassify = loading_button(self.alert, self.reclassify_btn, debug=True)(
            self.reclassify
        )
        self.get_reclassify_table = loading_button(
            self.alert, self.get_table, debug=True
        )(self.get_reclassify_table)
        self.load_matrix_content = loading_button(
            self.alert, self.import_table, debug=True
        )(self.load_matrix_content)

        # JS Events
        self.import_table.on_event("click", lambda *args: self.import_dialog.show())
        self.import_dialog.load_btn.on_event("click", self.load_matrix_content)
        self.save_table.on_event(
            "click", lambda *args: self.save_dialog.show(self.model.matrix)
        )
        self.w_image.observe(self._update_band, "v_model")
        self.get_table.on_event("click", self.get_reclassify_table)
        self.reclassify_btn.on_event("click", self.reclassify)
        [btn.on_event("click", self._set_dst_class_file) for btn in self.btn_list]

    def _set_dst_class_file(self, widget, event, data):
        """Set the destination classification according to the one selected with btn. alter the widgets properties to reflect this change"""

        # get the filename
        filename = widget._metadata["path"]

        if filename == "custom":
            self.w_dst_class_file.show()
        else:
            self.w_dst_class_file.hide()
            self.w_dst_class_file.select_file(filename)

        # change the visibility of the btns
        for btn in self.btn_list:
            btn.outlined = False if btn == widget else True

        return self

    def load_matrix_content(self, widget, event, data):
        """
        Load the content of the file in the matrix. The table need to be already set to perform this operation

        Return:
            self
        """
        self.import_dialog.value = False
        file = self.import_dialog.w_file.v_model

        # exit if no files are selected
        if not file:
            raise Exception("No file has been selected")

        # exit if no table is loaded
        if not self.model.table_created:
            raise Exception("You have to get the table before.")

        # load the file
        # sanity checks
        input_data = pd.read_csv(file).fillna(NO_VALUE)

        try:
            input_data.astype("int64")
        except Exception:
            raise Exception(
                "This file may contain non supported charaters for reclassification."
            )

        if len(input_data.columns) != 2:
            # Try to identify the oclumns and subset them
            if all([colname in list(input_data.columns) for colname in MATRIX_NAMES]):
                input_data = input_data[MATRIX_NAMES]
            else:
                raise Exception(
                    "This file is not a properly formatted as classification matrix"
                )

        # check that the destination values are all available
        widget = list(self.reclassify_table.class_select_list.values())[0]
        classes = [i["value"] for i in widget.items]
        if not all(v in classes for v in input_data.dst.unique()):
            raise Exception(
                "Some of the destination data are not existing in the destination dataset"
            )
        # fill the data
        for _, row in input_data.iterrows():
            src_code, dst_code = row.src, row.dst
            if str(src_code) in self.reclassify_table.class_select_list:
                self.reclassify_table.class_select_list[
                    str(src_code)
                ].v_model = dst_code

        self.import_dialog.w_file.reset()

        return self

    def reclassify(self, widget, event, data):
        """
        Reclassify the input and store it in the appropriate format.
        The input is not saved locally to avoid memory overload.

        Return:
            self
        """

        # create the output file
        msg = self.model.reclassify()

        # display a message to the user
        self.alert.add_msg(msg, "success")

        return self

    @su.switch("loading", "disabled", on_widgets=["w_code"])
    def _update_band(self, change):
        """Update the band possibility to the available bands/properties of the input"""

        # guess the file type and save it in the model
        self.model.get_type()
        # update the bands values
        self.w_code.v_model = None
        self.w_code.items = self.model.get_bands()

        return self

    @su.switch("disabled", on_widgets=["reclassify_btn"], targets=[False])
    @su.switch("table_created", on_widgets=["model"], targets=[True])
    def get_reclassify_table(self, widget, event, data):
        """
        Display a reclassify table which will lead the user to select
        a local code 'from user' to a target code based on a classes file

        Return:
            self
        """

        # get the destination classes
        self.model.dst_class = self.model.get_classes()

        # get the src_classes
        self.model.src_class = self.model.unique()

        # if the src_class_file is set overwrite src_class:
        if self.w_src_class_file.v_model:
            self.model.src_class = self.model.get_classes()

        # reset the table
        self.reclassify_table.set_table(self.model.dst_class, self.model.src_class)

        # check if the duplicate_layout need to be displayed ?
        self.duplicate_layout.class_ = "d-none"
        if len(self.reclassify_table.children[0].children) - 1 > self.MAX_CLASS:
            self.duplicate_layout.class_ = "d-block"

        return self

    def nest_tile(self):
        """
        Prepare the view to be used as a nested component in a tile.
        the elevation will be set to 0 and the title remove from children.
        The mount_id will also be changed to nested

        Return:
            self
        """

        # remove id
        self._metadata["mount_id"] = "nested_tile"

        # remove elevation
        self.elevation = False

        # remove title
        without_title = self.children.copy()
        without_title.remove(self.title)
        self.children = without_title

        return self
