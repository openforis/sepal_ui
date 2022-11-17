import json
from datetime import datetime
from pathlib import Path

import ee
import geopandas as gpd
import ipyvuetify as v
import pandas as pd
from deprecated.sphinx import versionadded
from ipywidgets import jslink
from natsort import humansorted
from traitlets import Any, Bool, Dict, Int, List, Unicode, link, observe

from sepal_ui import color
from sepal_ui.frontend import styles as ss
from sepal_ui.message import ms
from sepal_ui.scripts import gee
from sepal_ui.scripts import utils as su
from sepal_ui.sepalwidgets.btn import Btn
from sepal_ui.sepalwidgets.sepalwidget import SepalWidget

__all__ = [
    "DatePicker",
    "FileInput",
    "LoadTableField",
    "AssetSelect",
    "PasswordField",
    "NumberField",
    "VectorField",
]


@versionadded(
    version="2.13.0",
    reason="Empty v_model will be treated as empty string: :code:`v_model=''`.",
)
class DatePicker(v.Layout, SepalWidget):
    """
    Custom input widget to provide a reusable DatePicker. It allows to choose date as a string in the following format YYYY-MM-DD

    Args:
        label (str, optional): the label of the datepicker field
        layout_kwargs (dict, optional): any parameter for the wrapper layout
        kwargs (optional): any parameter from a v.DatePicker abject.

    """

    menu = None
    "v.Menu: the menu widget to display the datepicker"

    date_text = None
    "v.TextField: the text field of the datepicker widget"

    disabled = Bool(False).tag(sync=True)
    "traitlets.Bool: the disabled status of the Datepicker object"

    def __init__(self, label="Date", layout_kwargs={}, **kwargs):

        kwargs["v_model"] = kwargs.get("v_model", "")

        # create the widgets
        self.date_picker = v.DatePicker(no_title=True, scrollable=True, **kwargs)

        self.date_text = v.TextField(
            label=label,
            hint="YYYY-MM-DD format",
            persistent_hint=True,
            prepend_icon="event",
            readonly=True,
            v_on="menuData.on",
        )

        self.menu = v.Menu(
            min_width="290px",
            transition="scale-transition",
            offset_y=True,
            v_model=False,
            close_on_content_click=False,
            children=[self.date_picker],
            v_slots=[
                {
                    "name": "activator",
                    "variable": "menuData",
                    "children": self.date_text,
                }
            ],
        )

        # set the default parameter
        layout_kwargs["row"] = layout_kwargs.get("row", True)
        layout_kwargs["class_"] = layout_kwargs.get("class_", "pa-5")
        layout_kwargs["align_center"] = layout_kwargs.get("align_center", True)
        layout_kwargs["children"] = layout_kwargs.pop(
            "children", [v.Flex(xs10=True, children=[self.menu])]
        )

        # call the constructor
        super().__init__(**layout_kwargs)

        link((self.date_picker, "v_model"), (self.date_text, "v_model"))
        link((self.date_picker, "v_model"), (self, "v_model"))

    @observe("v_model")
    def check_date(self, change):
        """
        A method to check if the value of the set v_model is a correctly formated date
        Reset the widget and display an error if it's not the case
        """

        self.date_text.error_messages = None

        # exit immediately if nothing is set
        if not change["new"]:
            return

        # change the error status
        if not self.is_valid_date(change["new"]):
            msg = self.date_text.hint
            self.date_text.error_messages = msg

        return

    @observe("v_model")
    def close_menu(self, change):
        """A method to close the menu of the datepicker programatically"""

        # set the visibility
        self.menu.v_model = False

        return

    @observe("disabled")
    def disable(self, change):
        """A method to disabled the appropriate components in the datipkcer object"""

        self.menu.v_slots[0]["children"].disabled = self.disabled

        return

    @staticmethod
    def is_valid_date(date):
        """
        Check if the date is provided using the date format required for the widget

        Args:
            date (str): the date to test in YYYY-MM-DD format

        Return:
            (bool): the date to test
        """

        try:
            date = datetime.strptime(date, "%Y-%m-%d")
            valid = True

        except Exception:
            valid = False

        return valid


class FileInput(v.Flex, SepalWidget):
    """
    Custom input field to select a file in the sepal folders.

    Args:
        extentions ([str]): the list of the allowed extentions. the FileInput will only display these extention and folders
        folder (str | pathlib.Path): the starting folder of the file input
        label (str): the label of the input
        v_model (str, optional): the default value
        clearable (bool, optional): wether or not to make the widget clearable. default to False
        kwargs (optional): any parameter from a v.Flex abject. If set, 'children' will be overwritten.
    """

    extentions = []
    "list: the extention list"

    folder = Path.home()
    "pathlib.Path: the current folder"

    file = Any("").tag(sync=True)
    "str: the current file"

    selected_file = None
    "v.TextField: the textfield where the file pathname is stored"

    loading = None
    "v.ProgressLinear: loading top bar of the menu component"

    file_list = None
    "v.List: the list of files and folder that are available in the current folder"

    file_menu = None
    "v.Menu: the menu that hide and show the file_list"

    reload = None
    "v.Btn: reload btn to reload the file list on the current folder"

    clear = None
    "v.Btn: clear btn to remove everything and set back to the ini folder"

    v_model = Unicode(None, allow_none=True).tag(sync=True)
    "str: the v_model of the input"

    ICON_STYLE = json.loads((ss.JSON_DIR / "file_icons.json").read_text())
    "dict: the style applied to the icons in the file menu"

    def __init__(
        self,
        extentions=[],
        folder=Path.home(),
        label=ms.widgets.fileinput.label,
        v_model=None,
        clearable=False,
        **kwargs,
    ):

        if type(folder) == str:
            folder = Path(folder)

        self.extentions = extentions
        self.folder = folder

        self.selected_file = v.TextField(
            readonly=True,
            label=ms.widgets.fileinput.placeholder,
            class_="ml-5 mt-5",
            v_model=None,
        )

        p_style = json.loads((ss.JSON_DIR / "progress_bar.json").read_text())
        self.loading = v.ProgressLinear(
            indeterminate=False,
            background_color=color.menu,
            color=p_style["color"][v.theme.dark],
        )

        self.file_list = v.List(
            dense=True,
            color=color.menu,
            flat=True,
            v_model=True,
            max_height="300px",
            style_="overflow: auto;",
            children=[v.ListItemGroup(children=self._get_items(), v_model="")],
        )

        self.file_menu = v.Menu(
            min_width="400px",
            max_width="400px",
            children=[self.loading, self.file_list],
            v_model=False,
            close_on_content_click=False,
            v_slots=[
                {
                    "name": "activator",
                    "variable": "x",
                    "children": Btn(
                        icon="fas fa-search", v_model=False, v_on="x.on", text=label
                    ),
                }
            ],
        )

        self.reload = v.Btn(
            icon=True, color="primary", children=[v.Icon(children=["fas fa-sync-alt"])]
        )

        self.clear = v.Btn(
            icon=True, color="primary", children=[v.Icon(children=["fas fa-times"])]
        )
        if not clearable:
            su.hide_component(self.clear)

        # set default parameters
        kwargs["row"] = kwargs.pop("row", True)
        kwargs["class_"] = kwargs.pop("class_", "d-flex align-center mb-2")
        kwargs["align_center"] = kwargs.pop("align_center", True)
        kwargs["children"] = [
            self.clear,
            self.reload,
            self.file_menu,
            self.selected_file,
        ]

        # call the constructor
        super().__init__(**kwargs)

        link((self.selected_file, "v_model"), (self, "file"))
        link((self.selected_file, "v_model"), (self, "v_model"))

        self.file_list.children[0].observe(self._on_file_select, "v_model")
        self.reload.on_event("click", self._on_reload)
        self.clear.on_event("click", self.reset)

    def reset(self, *args):
        """
        Clear the File selection and move to the root folder.

        Return:
            self
        """

        # note: The args arguments are useless here but need to be kept so that
        # the function is natively compatible with the clear btn

        # do nothing if nothing is set to avoids extremelly long waiting
        # time when multiple fileInput are reset at the same time as in the aoiView
        if self.v_model is not None:

            # move to root
            self._on_file_select({"new": Path.home()})

            # remove v_model
            self.v_model = None

        return self

    def select_file(self, path):
        """
        Manually select a file from it's path. No verification on the extension is performed

        Params:
            path (str|pathlib.Path): the path to the file

        Return:
            self
        """

        # cast to Path
        path = Path(path)

        # test file existence
        if not path.is_file():
            raise Exception(f"{path} is not a file")

        # set the menu to the folder of the file
        self._on_file_select({"new": path.parent})

        # select the appropriate file
        self._on_file_select({"new": path})

        return self

    def _on_file_select(self, change):
        """Dispatch the behavior between file selection and folder change"""

        if not change["new"]:
            return self

        new_value = Path(change["new"])

        if new_value.is_dir():
            self.folder = new_value
            self._change_folder()

        elif new_value.is_file():
            self.file = str(new_value)

        return self

    @su.switch("indeterminate", on_widgets=["loading"])
    def _change_folder(self):
        """Change the target folder"""

        # get the items
        items = self._get_items()

        # reset files
        # this is reseting the scroll to top without using js scripts
        self.file_list.children[0].children = []

        # set the new files
        self.file_list.children[0].children = items

        return

    def _get_items(self):
        """Return the list of items inside the folder"""

        folder = self.folder

        list_dir = [el for el in folder.glob("*/") if not el.name.startswith(".")]

        if self.extentions:
            list_dir = [
                el for el in list_dir if el.is_dir() or el.suffix in self.extentions
            ]

        folder_list = []
        file_list = []

        for el in list_dir:

            if el.is_dir():
                icon = self.ICON_STYLE[""]["icon"]
                color = self.ICON_STYLE[""]["color"][v.theme.dark]
            elif el.suffix in self.ICON_STYLE.keys():
                icon = self.ICON_STYLE[el.suffix]["icon"]
                color = self.ICON_STYLE[el.suffix]["color"][v.theme.dark]
            else:
                icon = self.ICON_STYLE["DEFAULT"]["icon"]
                color = self.ICON_STYLE["DEFAULT"]["color"][v.theme.dark]

            children = [
                v.ListItemAction(children=[v.Icon(color=color, children=[icon])]),
                v.ListItemContent(
                    children=[v.ListItemTitle(children=[el.stem + el.suffix])]
                ),
            ]

            if el.is_dir():
                folder_list.append(v.ListItem(value=str(el), children=children))
            else:
                file_size = su.get_file_size(el)
                children.append(
                    v.ListItemActionText(class_="ml-1", children=[file_size])
                )
                file_list.append(v.ListItem(value=str(el), children=children))

        folder_list = humansorted(folder_list, key=lambda x: x.value)
        file_list = humansorted(file_list, key=lambda x: x.value)

        parent_item = v.ListItem(
            value=str(folder.parent),
            children=[
                v.ListItemAction(
                    children=[
                        v.Icon(
                            color=self.ICON_STYLE["PARENT"]["color"][v.theme.dark],
                            children=[self.ICON_STYLE["PARENT"]["icon"]],
                        )
                    ]
                ),
                v.ListItemContent(
                    children=[v.ListItemTitle(children=[f".. /{folder.parent.stem}"])]
                ),
            ],
        )

        folder_list.extend(file_list)
        folder_list.insert(0, parent_item)

        return folder_list

    def _on_reload(self, widget, event, data):

        # force the update of the current folder
        self._change_folder()

        return

    @observe("v_model")
    def close_menu(self, change):
        """A method to close the menu of the Fileinput programatically"""

        # set the visibility
        self.file_menu.v_model = False

        return


class LoadTableField(v.Col, SepalWidget):
    """
    A custom input widget to load points data. The user will provide a csv or txt file containing labeled dataset.
    The relevant columns (lat, long and id) can then be identified in the updated select. Once everything is set, the widget will populate itself with a json dict.
    {pathname, id_column, lat_column,lng_column}

    Args:
        label (str, optional): the label of the widget
        kwargs (optional): any parameter from a v.Col. If set, 'children' and 'v_model' will be overwritten.
    """

    fileInput = None
    "sw.FileInput: the file input to select the .csv or .txt file"

    IdSelect = None
    "v.Select: input to select the id column"

    LngSelect = None
    "v.Select: input to select the lng column"

    LatSelect = None
    "v.Select: input to select the lat column"

    default_v_model = {
        "pathname": None,
        "id_column": None,
        "lat_column": None,
        "lng_column": None,
    }
    "dict: The default v_model structure {'pathname': xx, 'id_column': xx, 'lat_column': xx, 'lng_column': xx}"

    def __init__(self, label=ms.widgets.table.label, **kwargs):

        self.fileInput = FileInput([".csv", ".txt"], label=label)

        self.IdSelect = v.Select(
            _metadata={"name": "id_column"},
            items=[],
            label=ms.widgets.table.column.id,
            v_model=None,
        )
        self.LngSelect = v.Select(
            _metadata={"name": "lng_column"},
            items=[],
            label=ms.widgets.table.column.lng,
            v_model=None,
        )
        self.LatSelect = v.Select(
            _metadata={"name": "lat_column"},
            items=[],
            label=ms.widgets.table.column.lat,
            v_model=None,
        )

        # set default parameters
        kwargs["v_model"] = self.default_v_model  # format of v_model is fixed
        kwargs["children"] = [
            self.fileInput,
            self.IdSelect,
            self.LngSelect,
            self.LatSelect,
        ]

        # call the constructor
        super().__init__(**kwargs)

        # link the dropdowns
        jslink((self.IdSelect, "items"), (self.LngSelect, "items"))
        jslink((self.IdSelect, "items"), (self.LatSelect, "items"))

        # link the widget with v_model
        self.fileInput.observe(self._on_file_input_change, "v_model")
        self.IdSelect.observe(self._on_select_change, "v_model")
        self.LngSelect.observe(self._on_select_change, "v_model")
        self.LatSelect.observe(self._on_select_change, "v_model")

    def reset(self):
        """
        Clear the values and return to the empty default json

        Return:
            self
        """

        # clear the fileInput
        self.fileInput.reset()

        return

    @su.switch("loading", on_widgets=["IdSelect", "LngSelect", "LatSelect"])
    def _on_file_input_change(self, change):
        """Update the select content when the fileinput v_model is changing"""

        # clear the selects
        self._clear_select()

        # set the path
        path = change["new"]
        self._set_v_model("pathname", path)

        # exit if none
        if path is None:
            return self

        df = pd.read_csv(path, sep=None, engine="python")

        if len(df.columns) < 3:
            self._set_v_model("pathname", None)
            self.fileInput.selected_file.error_messages = (
                ms.widgets.load_table.too_small
            )
            return

        # set the items
        self.IdSelect.items = df.columns.tolist()

        # pre load values that sounds like what we are looking for
        # it will only keep the first occurence of each one
        for name in reversed(df.columns.tolist()):
            lname = name.lower()
            if "id" in lname:
                self.IdSelect.v_model = name
            elif any(
                ext in lname
                for ext in ["lng", "long", "longitude", "x_coord", "xcoord", "lon"]
            ):
                self.LngSelect.v_model = name
            elif any(ext in lname for ext in ["lat", "latitude", "y_coord", "ycoord"]):
                self.LatSelect.v_model = name

        return self

    def _clear_select(self):
        """clear the selects components"""

        self.fileInput.selected_file.error_messages = None
        self.IdSelect.items = []  # all the others are listening to this one
        self.IdSelect.v_model = self.LngSelect.v_model = self.LatSelect.v_model = None

        return self

    def _on_select_change(self, change):
        """change the v_model value when a select is changed"""

        name = change["owner"]._metadata["name"]
        self._set_v_model(name, change["new"])

        return self

    def _set_v_model(self, key, value):
        """
        set the v_model from an external function to trigger the change event

        Args:
            key (str): the column name
            value (any): the new value to set
        """

        tmp = self.v_model.copy()
        tmp[key] = value
        self.v_model = tmp

        return


class AssetSelect(v.Combobox, SepalWidget):
    """
    Custom widget input to select an asset inside the asset folder of the user

    Args:
        label (str): the label of the input
        folder (str): the folder of the user assets
        default_asset (str, list): the id of a default asset or a list of defaults
        types ([str]): the list of asset type you want to display to the user. type need to be from: ['IMAGE', 'FOLDER', 'IMAGE_COLLECTION', 'TABLE','ALGORITHM']. Default to 'IMAGE' & 'TABLE'
        kwargs (optional): any parameter from a v.ComboBox.
    """

    TYPES = {
        "IMAGE": ms.widgets.asset_select.types[0],
        "TABLE": ms.widgets.asset_select.types[1],
        "IMAGE_COLLECTION": ms.widgets.asset_select.types[2],
        "ALGORITHM": ms.widgets.asset_select.types[3],
        "FOLDER": ms.widgets.asset_select.types[4],
        # UNKNOWN type is ignored
    }
    "dict: Valid ypes of asset"

    folder = None
    "str: the folder of the user assets, mainly for debug"

    valid = True
    "Bool: whether the selected asset is valid (user has access) or not"

    asset_info = {}
    "dict: The selected asset informations"

    default_asset = Any().tag(sync=True)
    "str: the id of a default asset or a list of default assets"

    types = List().tag(sync=True)
    "List: the list of types accepted by the asset selector. names need to be valide TYPES and changing this value will trigger the reload of the asset items."

    @su.need_ee
    def __init__(
        self,
        label=ms.widgets.asset_select.label,
        folder=None,
        types=["IMAGE", "TABLE"],
        default_asset=[],
        **kwargs,
    ):
        self.valid = False
        self.asset_info = None

        # if folder is not set use the root one
        self.folder = folder if folder else ee.data.getAssetRoots()[0]["id"]
        self.types = types

        # load the default assets
        self.default_asset = default_asset

        # Validate the input as soon as the object is instantiated
        self.observe(self._validate, "v_model")

        # set the default parameters
        kwargs["v_model"] = kwargs.pop("v_model", None)
        kwargs["clearable"] = kwargs.pop("clearable", True)
        kwargs["dense"] = kwargs.pop("dense", True)
        kwargs["prepend_icon"] = kwargs.pop("prepend_icon", "mdi-sync")
        kwargs["class_"] = kwargs.pop("class_", "my-5")
        kwargs["placeholder"] = kwargs.pop(
            "placeholder", ms.widgets.asset_select.placeholder
        )

        # create the widget
        super().__init__(**kwargs)

        # load the assets in the combobox
        self._get_items()

        # add js behaviours
        self.on_event("click:prepend", self._get_items)
        self.observe(self._get_items, "default_asset")

    @su.switch("loading")
    def _validate(self, change):
        """
        Validate the selected asset. Throw an error message if is not accesible or not in the type list.
        """

        self.error_messages = None

        if change["new"]:

            # check that the asset can be accessed
            try:
                self.asset_info = ee.data.getAsset(change["new"])

                # check that the asset has the correct type
                if not self.asset_info["type"] in self.types:
                    self.error_messages = ms.widgets.asset_select.wrong_type.format(
                        self.asset_info["type"], ",".join(self.types)
                    )

            except Exception:

                self.error_messages = ms.widgets.asset_select.no_access

            self.valid = self.error_messages is None
            self.error = self.error_messages is not None

        return

    @su.switch("loading", "disabled")
    def _get_items(self, *args):

        # init the item list
        items = []

        # add the default values if needed
        if self.default_asset:

            if isinstance(self.default_asset, str):
                self.default_asset = [self.default_asset]

            self.v_model = self.default_asset[0]

            header = ms.widgets.asset_select.custom
            items += [{"divider": True}, {"header": header}]
            items += [default for default in self.default_asset]

        # get the list of user asset
        raw_assets = gee.get_assets(self.folder)
        assets = {
            k: sorted([e["id"] for e in raw_assets if e["type"] == k])
            for k in self.types
        }

        # sort the assets by types
        for k in self.types:
            if len(assets[k]):
                items += [
                    {"divider": True},
                    {"header": self.TYPES[k]},
                    *assets[k],
                ]

        self.items = items

        return self

    @observe("types")
    def _check_types(self, change):
        """clean the type list, keeping only the valid one"""

        self.v_model = None

        # check the type
        self.types = [t for t in self.types if t in self.TYPES]

        # trigger the reload
        self._get_items()

        return


class PasswordField(v.TextField, SepalWidget):
    """
    Custom widget to input passwords in text area and
    toggle its visibility.

    Args:
        label (str, optional): Header displayed in text area. Defaults to Password.
        kwargs (dict); any parameter from a v.TextField. If set, 'type' will be overwritten.
    """

    def __init__(self, **kwargs):

        # default behavior
        kwargs["label"] = kwargs.pop("label", "Password")
        kwargs["class_"] = kwargs.pop("class_", "mr-2")
        kwargs["v_model"] = kwargs.pop("v_model", "")
        kwargs["type"] = "password"
        kwargs["append_icon"] = kwargs.pop("append_icon", "mdi-eye-off")

        # init the widget with the remaining kwargs
        super().__init__(**kwargs)

        # bind the js behavior
        self.on_event("click:append", self._toggle_pwd)

    def _toggle_pwd(self, widget, event, data):
        """Toggle password visibility when append button is clicked"""

        if self.type == "text":
            self.type = "password"
            self.append_icon = "mdi-eye-off"
        else:
            self.type = "text"
            self.append_icon = "mdi-eye"


class NumberField(v.TextField, SepalWidget):
    """
    Custom widget to input numbers in text area and add/substract with single increment.

    Args:
        max_ (int, optional): Maximum selectable number. Defaults to 10.
        min_ (int, optional): Minimum selectable number. Defaults to 0.
        increm (int, optional): incremental value added at each step. default to 1
        kwargs (dict, optional): Any parameter from a v.TextField. If set, 'type' will be overwritten.
    """

    max_ = Int(10).tag(sync=True)
    "int: Maximum selectable number."

    min_ = Int(0).tag(sync=True)
    "int: Minimum selectable number."

    increm = Int(1).tag(sync=True)
    "int: incremental value added at each step."

    def __init__(self, max_=10, min_=0, increm=1, **kwargs):

        # set the traits
        self.max_ = max_
        self.min_ = min_
        self.increm = increm

        # set default params
        kwargs["type"] = "number"
        kwargs["append_outer_icon"] = kwargs.pop("append_outer_icon", "mdi-plus")
        kwargs["prepend_icon"] = kwargs.pop("prepend_icon", "mdi-minus")
        kwargs["v_model"] = kwargs.pop("v_model", 0)
        kwargs["readonly"] = kwargs.pop("readonly", True)

        # call the constructor
        super().__init__(**kwargs)

        self.on_event("click:append-outer", self.increment)
        self.on_event("click:prepend", self.decrement)

    def increment(self, widget, event, data):
        """Adds increm to the current v_model number"""

        self.v_model = min((self.v_model + self.increm), self.max_)

        return

    def decrement(self, widget, event, data):
        """Substracts increm to the current v_model number"""

        self.v_model = max((self.v_model - self.increm), self.min_)

        return


class VectorField(v.Col, SepalWidget):
    """
    A custom input widget to load vector data. The user will provide a vector file compatible with fiona or a GEE feature collection.
    The user can then select a specific shape by setting column and value fields.

    Args:
        label (str): the label of the file input field, default to 'vector file'.
        gee (bool, optional): whether to use GEE assets or local vectors.
        folder (str, optional): When gee=True, extra args will be used for AssetSelect
        kwargs (dict, optional): any parameter from a v.Col. if set, 'children' will be overwritten.
    """

    original_gdf = None
    "geopandas.GeoDataframe: The originally selected dataframe"

    df = None
    "pandas.Dataframe: the orginal dataframe without the geometry (for column naming)"

    gdf = None
    "geopandas.GeoDataframe: The selected dataframe"

    w_file = None
    "sw.FileInput: The file selector widget"

    w_column = None
    "v.Select: The Select widget to select the column"

    w_value = None
    "v.Select: The Select widget to select the value in the selected column"

    v_model = Dict(
        {
            "pathname": None,
            "column": None,
            "value": None,
        }
    )
    "Traitlet: The json saved v_model shaped as {'pathname': xx, 'column': xx, 'value': xx}"

    column_base_items = [
        {"text": ms.widgets.vector.all, "value": "ALL"},
        {"divider": True},
    ]
    "list: the column compulsory selector (ALL)"

    feature_collection = None
    "ee.FeatureCollection: the selected featureCollection"

    def __init__(self, label=ms.widgets.vector.label, gee=False, **kwargs):

        # set the 3 wigets
        if not gee:
            self.w_file = FileInput([".shp", ".geojson", ".gpkg", ".kml"], label=label)
        else:
            # Don't care about 'types' arg. It will only work with tables.
            asset_select_kwargs = {"folder": kwargs.pop("folder", None)}
            self.w_file = AssetSelect(types=["TABLE"], **asset_select_kwargs)

        self.w_column = v.Select(
            _metadata={"name": "column"},
            items=self.column_base_items,
            label=ms.widgets.vector.column,
            v_model="ALL",
        )
        self.w_value = v.Select(
            _metadata={"name": "value"},
            items=[],
            label=ms.widgets.vector.value,
            v_model=None,
        )
        su.hide_component(self.w_value)

        # create the Col Field
        kwargs["children"] = [self.w_file, self.w_column, self.w_value]

        super().__init__(**kwargs)

        # events
        self.w_file.observe(self._update_file, "v_model")
        self.w_column.observe(self._update_column, "v_model")
        self.w_value.observe(self._update_value, "v_model")

    def reset(self):
        """
        Return the field to its initial state

        Return:
            self
        """

        self.w_file.reset()

        return self

    @su.switch("loading", on_widgets=["w_column", "w_value"])
    def _update_file(self, change):
        """update the file name, the v_model and reset the other widgets"""

        # reset the widgets
        self.w_column.items, self.w_value.items = [], []
        self.w_column.v_model = self.w_value.v_model = None
        self.df = None
        self.feature_collection = None

        # set the pathname value
        self._set_v_model("pathname", change["new"])

        # exit if nothing
        if not change["new"]:
            return self

        if isinstance(self.w_file, FileInput):
            # read the file
            self.df = gpd.read_file(change["new"], ignore_geometry=True)
            columns = self.df.columns.to_list()

        elif isinstance(self.w_file, AssetSelect):
            self.feature_collection = ee.FeatureCollection(change["new"])
            columns = self.feature_collection.first().getInfo()["properties"]
            columns = [
                str(col) for col in columns if col not in ["system:index", "Shape_Area"]
            ]

        # update the columns
        self.w_column.items = self.column_base_items + sorted(set(columns))

        self.w_column.v_model = "ALL"

        return self

    @su.switch("loading", on_widgets=["w_value"])
    def _update_column(self, change):
        """Update the column name and empty the value list"""

        # set the value
        self._set_v_model("column", change["new"])

        # exit if nothing as the only way to set this value to None is the reset
        if not change["new"]:
            return self

        # reset value widget
        self.w_value.items = []
        self.w_value.v_model = None

        # hide value if "ALL" or none
        if change["new"] in ["ALL", None]:
            su.hide_component(self.w_value)
            return self

        # read the colmun
        if isinstance(self.w_file, FileInput):
            values = self.df[change["new"]].to_list()

        elif isinstance(self.w_file, AssetSelect):
            values = (
                self.feature_collection.distinct(change["new"])
                .aggregate_array(change["new"])
                .getInfo()
            )

        self.w_value.items = sorted(set(values))

        su.show_component(self.w_value)

        return self

    def _update_value(self, change):
        """Update the value name and reduce the gdf"""

        # set the value
        self._set_v_model("value", change["new"])

        return self

    def _set_v_model(self, key, value):
        """
        set the v_model from an external function to trigger the change event

        Args:
            key (str): the column name
            value (any): the new value to set
        """

        tmp = self.v_model.copy()
        tmp[key] = value
        self.v_model = tmp

        return
