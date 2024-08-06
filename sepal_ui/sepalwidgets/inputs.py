"""Custom input widgets to setup parameters in application.

Gather the customized ``ipyvuetifyWidgets`` used to create input fields in applications.
All the content of this modules is included in the parent ``sepal_ui.sepalwidgets`` package. So it can be imported directly from there.

Example:
    .. jupyter-execute::

        from sepal_ui import sepalwidgets as sw

        sw.DatePicker()
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Union

import ee
import geopandas as gpd
import ipyvuetify as v
import pandas as pd
import traitlets as t
from deprecated.sphinx import versionadded
from natsort import humansorted
from traitlets import link, observe
from typing_extensions import Self

from sepal_ui.frontend import styles as ss
from sepal_ui.message import ms
from sepal_ui.scripts import decorator as sd
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
    "SimpleSlider",
]


@versionadded(
    version="2.13.0",
    reason="Empty v_model will be treated as empty string: :code:`v_model=''`.",
)
class DatePicker(v.Layout, SepalWidget):
    menu: Optional[v.Menu] = None
    "the menu widget to display the datepicker"

    date_text: Optional[v.TextField] = None
    "the text field of the datepicker widget"

    disabled: t.Bool = t.Bool(False).tag(sync=True)
    "the disabled status of the Datepicker object"

    def __init__(self, label: str = "Date", layout_kwargs: Optional[dict] = None, **kwargs) -> None:
        """Custom input widget to provide a reusable DatePicker.

        It allows to choose date as a string in the following format YYYY-MM-DD.

        Args:
            label: the label of the datepicker field
            layout_kwargs: any parameter for the wrapper v.Layout
            kwargs: any parameter from a v.DatePicker object.
        """
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
        layout_kwargs = layout_kwargs or {}
        layout_kwargs.setdefault("row", True)
        layout_kwargs.setdefault("class_", "pa-5")
        layout_kwargs.setdefault("align_center", True)
        layout_kwargs.setdefault("children", [v.Flex(xs10=True, children=[self.menu])])

        # call the constructor
        super().__init__(**layout_kwargs)

        link((self.date_picker, "v_model"), (self.date_text, "v_model"))
        link((self.date_picker, "v_model"), (self, "v_model"))

    @observe("v_model")
    def check_date(self, change: dict) -> None:
        """Check if the data is formatted date.

        A method to check if the value of the set v_model is a correctly formatted date
        Reset the widget and display an error if it's not the case.
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
    def close_menu(self, change: dict) -> None:
        """A method to close the menu of the datepicker programmatically."""
        # set the visibility
        self.menu.v_model = False

        return

    @observe("disabled")
    def disable(self, change: dict) -> None:
        """A method to disabled the appropriate components in the datipkcer object."""
        self.menu.v_slots[0]["children"].disabled = self.disabled

        return

    def today(self) -> Self:
        """Update the date to the current day."""
        self.v_model = datetime.today().strftime("%Y-%m-%d")

        return self

    @staticmethod
    def is_valid_date(date: str) -> bool:
        """Check if the date is provided using the date format required for the widget.

        Args:
            date: the date to test in YYYY-MM-DD format

        Returns:
            The validity of the date with respect to the datepicker format
        """
        valid = True
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except (ValueError, TypeError):
            valid = False

        return valid


class FileInput(v.Flex, SepalWidget):
    extensions: List[str] = []
    "list: the extensions list"

    folder: Path = Path.home()
    "the current folder"

    initial_folder: Path = Path.home()
    "the starting point of the file input"

    file: t.Unicode = t.Unicode("").tag(sync=True)
    "the current file"

    selected_file: Optional[v.TextField] = None
    "the textfield where the file pathname is stored"

    loading: Optional[v.ProgressLinear] = None
    "loading top bar of the menu component"

    file_list: Optional[v.List] = None
    "the list of files and folder that are available in the current folder"

    file_menu: Optional[v.Menu] = None
    "the menu that hide and show the file_list"

    reload: Optional[v.Btn] = None
    "reload btn to reload the file list on the current folder"

    clear: Optional[v.Btn] = None
    "clear btn to remove everything and set back to the ini folder"

    root: t.Unicode = t.Unicode("").tag(sync=True)
    "the root folder from which you cannot go higher in the tree."

    v_model: t.Unicode = t.Unicode(None, allow_none=True).tag(sync=True)
    "the v_model of the input"

    ICON_STYLE: dict = json.loads((ss.JSON_DIR / "file_icons.json").read_text())
    "the style applied to the icons in the file menu"

    def __init__(
        self,
        extensions: List[str] = [],
        folder: Union[str, Path] = Path.home(),
        label: str = ms.widgets.fileinput.label,
        v_model: str = "",
        clearable: bool = False,
        root: Union[str, Path] = "",
        cache=False,
        **kwargs,
    ) -> None:
        """Custom input field to select a file in the sepal folders.

        Args:
            extensions: the list of the allowed extensions. the FileInput will only display these extension and folders
            folder: the starting folder of the file input
            label: the label of the input
            v_model: the default value
            clearable: whether or not to make the widget clearable. default to False
            root: the root folder from which you cannot go higher in the tree.
            kwargs: any parameter from a v.Flex abject. If set, 'children' will be overwritten.
        """
        self.extensions = extensions
        self.initial_folder = folder
        self.folder = Path(folder)
        self.root = str(root) if isinstance(root, Path) else root
        self.cache_dirs = {}

        self.selected_file = v.TextField(
            readonly=True,
            label=ms.widgets.fileinput.placeholder,
            class_="ml-5 mt-5",
            v_model="",
        )

        self.loading = v.ProgressLinear(
            indeterminate=False,
            background_color="menu",
        )

        self.file_list = v.List(
            dense=True,
            color="menu",
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
                        gliph="fa-solid fa-search",
                        v_model=False,
                        v_on="x.on",
                        msg=label,
                    ),
                }
            ],
        )

        self.reload = v.Btn(
            icon=True,
            color="primary",
            children=[v.Icon(children=["fa-solid fa-sync-alt"])],
        )

        self.clear = v.Btn(
            icon=True,
            color="primary",
            children=[v.Icon(children=["fa-solid fa-times"])],
        )
        if not clearable:
            su.hide_component(self.clear)

        # set default parameters
        kwargs.setdefault("row", True)
        kwargs.setdefault("class_", "d-flex align-center mb-2")
        kwargs.setdefault("align_center", True)
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

        # set the default v_model
        self.v_model = v_model

    def reset(self, *args) -> Self:
        """Clear the File selection and move to the root folder."""
        # note: The args arguments are useless here but need to be kept so that
        # the function is natively compatible with the clear btn

        # do nothing if nothing is set to avoids extremely long waiting
        # time when multiple fileInput are reset at the same time as in the aoiView
        if self.v_model is not None:
            # move to root
            self._on_file_select({"new": self.initial_folder})

            # remove v_model
            self.v_model = ""

        return self

    def select_file(self, path: Union[str, Path]) -> Self:
        """Manually select a file from it's path. No verification on the extension is performed.

        Args:
            path: the path to the file
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

    def _on_file_select(self, change: dict) -> Self:
        """Dispatch the behavior between file selection and folder change."""
        if not change["new"]:
            return self

        new_value = Path(change["new"])

        if new_value.is_dir():
            self.folder = new_value

            # don't change folder if the folder is the parent of the root
            if not self.folder == Path(self.root).parent:
                self._change_folder()

        elif new_value.is_file():
            self.file = str(new_value)

        return self

    @sd.switch("indeterminate", on_widgets=["loading"])
    def _change_folder(self) -> None:
        """Change the target folder."""
        # get the items
        items = self._get_items()

        # reset files
        # this is resetting the scroll to top without using js scripts
        self.file_list.children[0].children = []

        # set the new files
        self.file_list.children[0].children = items

        return

    def _get_items(self) -> List[v.ListItem]:
        """Create the list of items inside the folder.

        Returns:
            list of items inside the selected folder
        """
        folder = self.folder

        list_dir = [el for el in folder.glob("*") if not el.name.startswith(".")]

        if self.extensions:
            list_dir = [el for el in list_dir if el.is_dir() or el.suffix in self.extensions]

        if folder in self.cache_dirs:
            if self.cache_dirs[folder]["files"] == list_dir:
                return self.cache_dirs[folder]["items"]

        folder_list = []
        file_list = []

        for el in list_dir:
            if el.is_dir():
                icon = self.ICON_STYLE[""]["icon"]
                color = self.ICON_STYLE[""]["color"]
            elif el.suffix in self.ICON_STYLE.keys():
                icon = self.ICON_STYLE[el.suffix]["icon"]
                color = self.ICON_STYLE[el.suffix]["color"]
            else:
                icon = self.ICON_STYLE["DEFAULT"]["icon"]
                color = self.ICON_STYLE["DEFAULT"]["color"]

            children = [
                v.ListItemAction(children=[v.Icon(color=color, children=[icon])]),
                v.ListItemContent(children=[v.ListItemTitle(children=[el.stem + el.suffix])]),
            ]

            if el.is_dir():
                folder_list.append(v.ListItem(value=str(el), children=children))
            else:
                file_size = su.get_file_size(el)
                children.append(v.ListItemActionText(class_="ml-1", children=[file_size]))
                file_list.append(v.ListItem(value=str(el), children=children))

        folder_list = humansorted(folder_list, key=lambda x: x.value)
        file_list = humansorted(file_list, key=lambda x: x.value)

        parent_item = v.ListItem(
            value=str(folder.parent),
            children=[
                v.ListItemAction(
                    children=[
                        v.Icon(
                            color=self.ICON_STYLE["PARENT"]["color"],
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

        self.cache_dirs.setdefault(folder, {})
        self.cache_dirs[folder]["files"] = list_dir
        self.cache_dirs[folder]["items"] = folder_list

        return folder_list

    def _on_reload(self, *args) -> None:
        # force the update of the current folder
        self._change_folder()

        return

    @observe("v_model")
    def close_menu(self, change: dict) -> None:
        """A method to close the menu of the Fileinput programmatically."""
        # set the visibility
        self.file_menu.v_model = False

        return


class LoadTableField(v.Col, SepalWidget):
    fileInput: Optional[FileInput] = None
    "The file input to select the .csv or .txt file"

    IdSelect: Optional[v.Select] = None
    "input to select the id column"

    LngSelect: Optional[v.Select] = None
    "input to select the lng column"

    LatSelect: Optional[v.Select] = None
    "input to select the lat column"

    default_v_model: dict = {
        "pathname": None,
        "id_column": None,
        "lat_column": None,
        "lng_column": None,
    }
    "The default v_model structure {'pathname': xx, 'id_column': xx, 'lat_column': xx, 'lng_column': xx}"

    def __init__(self, label: str = ms.widgets.table.label, **kwargs) -> None:
        """A custom input widget to load points data.

        The user will provide a csv or txt file containing labeled dataset.
        The relevant columns (lat, long and id) can then be identified in the updated select. Once everything is set, the widget will populate itself with a json dict.
        {pathname, id_column, lat_column,lng_column}.

        Args:
            label: the label of the widget
            kwargs: any parameter from a v.Col. If set, 'children' and 'v_model' will be overwritten.
        """
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
        link((self.IdSelect, "items"), (self.LngSelect, "items"))
        link((self.IdSelect, "items"), (self.LatSelect, "items"))

        # link the widget with v_model
        self.fileInput.observe(self._on_file_input_change, "v_model")
        self.IdSelect.observe(self._on_select_change, "v_model")
        self.LngSelect.observe(self._on_select_change, "v_model")
        self.LatSelect.observe(self._on_select_change, "v_model")

    def reset(self) -> Self:
        """Clear the values and return to the empty default json."""
        # clear the fileInput
        self.fileInput.reset()

        return

    @sd.switch("loading", on_widgets=["IdSelect", "LngSelect", "LatSelect"])
    def _on_file_input_change(self, change: dict) -> Self:
        """Update the select content when the fileinput v_model is changing."""
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
            self.fileInput.selected_file.error_messages = ms.widgets.load_table.too_small
            return self

        # set the items
        self.IdSelect.items = df.columns.tolist()

        # pre load values that sounds like what we are looking for
        # it will only keep the first occurrence of each one
        for name in reversed(df.columns.tolist()):
            lname = name.lower()
            if "id" in lname:
                self.IdSelect.v_model = name
            elif any(
                ext in lname for ext in ["lng", "long", "longitude", "x_coord", "xcoord", "lon"]
            ):
                self.LngSelect.v_model = name
            elif any(ext in lname for ext in ["lat", "latitude", "y_coord", "ycoord"]):
                self.LatSelect.v_model = name

        return self

    def _clear_select(self) -> Self:
        """Clear the selects components."""
        self.fileInput.selected_file.error_messages = None
        self.IdSelect.items = []  # all the others are listening to this one
        self.IdSelect.v_model = self.LngSelect.v_model = self.LatSelect.v_model = None

        return self

    def _on_select_change(self, change: dict) -> Self:
        """Change the v_model value when a select is changed."""
        name = change["owner"]._metadata["name"]
        self._set_v_model(name, change["new"])

        return self

    def _set_v_model(self, key: str, value: Any) -> None:
        """set the v_model from an external function to trigger the change event.

        Args:
            key: the column name
            value: the new value to set
        """
        tmp = self.v_model.copy()
        tmp[key] = value
        self.v_model = tmp

        return


class AssetSelect(v.Combobox, SepalWidget):
    TYPES: dict = {
        "IMAGE": ms.widgets.asset_select.types[0],
        "TABLE": ms.widgets.asset_select.types[1],
        "IMAGE_COLLECTION": ms.widgets.asset_select.types[2],
        "ALGORITHM": ms.widgets.asset_select.types[3],
        "FOLDER": ms.widgets.asset_select.types[4],
        # UNKNOWN type is ignored
    }
    "Valid types of asset"

    folder: str = ""
    "the folder of the user assets, mainly for debug"

    valid: bool = True
    "whether the selected asset is valid (user has access) or not"

    asset_info: dict = {}
    "The selected asset information"

    default_asset: t.List = t.List([]).tag(sync=True)
    "The id of a default asset or a list of default assets"

    types: t.List = t.List().tag(sync=True)
    "The list of types accepted by the asset selector. names need to be valid TYPES and changing this value will trigger the reload of the asset items."

    @sd.need_ee
    def __init__(
        self,
        folder: Union[str, Path] = "",
        types: List[str] = ["IMAGE", "TABLE"],
        default_asset: Union[str, List[str]] = [],
        **kwargs,
    ) -> None:
        """Custom widget input to select an asset inside the asset folder of the user.

        Args:
            label: the label of the input
            folder: the folder of the user assets
            default_asset: the id of a default asset or a list of defaults
            types: the list of asset type you want to display to the user. type need to be from: ['IMAGE', 'FOLDER', 'IMAGE_COLLECTION', 'TABLE','ALGORITHM']. Default to 'IMAGE' & 'TABLE'
            kwargs (optional): any parameter from a v.ComboBox.
        """
        self.valid = False
        self.asset_info = None

        # if folder is not set use the root one
        self.folder = str(folder) or f"projects/{ee.data._cloud_api_user_project}/assets/"
        self.types = types

        # load the default assets
        self.default_asset = default_asset

        # Validate the input as soon as the object is instantiated
        self.observe(self._validate, "v_model")

        self.observe(self._fill_no_data, "items")

        # set the default parameters
        kwargs.setdefault("v_model", None)
        kwargs.setdefault("clearable", True)
        kwargs.setdefault("dense", True)
        kwargs.setdefault("prepend_icon", "mdi-sync")
        kwargs.setdefault("class_", "my-5")
        kwargs.setdefault("placeholder", ms.widgets.asset_select.placeholder)
        kwargs.setdefault("label", ms.widgets.asset_select.label)

        # create the widget
        super().__init__(**kwargs)

        # load the assets in the combobox
        self._get_items()

        self._fill_no_data({})

        # add js behaviours
        self.on_event("click:prepend", self._get_items)
        self.observe(self._get_items, "default_asset")

    def _fill_no_data(self, _: dict) -> None:
        """Fill the items with a no data message if the items are empty."""
        # Done in this way because v_slots are not working
        if not self.items:
            self.v_model = None
            self.items = [
                {
                    "text": ms.widgets.asset_select.no_assets.format(self.folder),
                    "disabled": True,
                }
            ]

        return

    @sd.switch("loading")
    def _validate(self, change: dict) -> None:
        """Validate the selected asset. Throw an error message if is not accessible or not in the type list."""
        self.error_messages = None

        # trim the current value
        if isinstance(self.v_model, str):
            self.v_model = self.v_model.strip()

        if change["new"]:
            # check that the asset can be accessed
            try:
                self.asset_info = ee.data.getAsset(self.v_model)

                # check that the asset has the correct type
                if self.asset_info["type"] not in self.types:
                    self.error_messages = ms.widgets.asset_select.wrong_type.format(
                        self.asset_info["type"], ",".join(self.types)
                    )

            except Exception:
                self.error_messages = ms.widgets.asset_select.no_access

            self.valid = self.error_messages is None
            self.error = self.error_messages is not None

        return

    @sd.switch("loading", "disabled")
    def _get_items(self, *args) -> Self:
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
        assets = {k: sorted([e["id"] for e in raw_assets if e["type"] == k]) for k in self.types}

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
    def _check_types(self, change: dict) -> None:
        """Clean the type list, keeping only the valid one."""
        self.v_model = None

        # check the type
        self.types = [t for t in self.types if t in self.TYPES]

        # trigger the reload
        self._get_items()

        return


class PasswordField(v.TextField, SepalWidget):
    def __init__(self, **kwargs) -> None:
        """Custom widget to input passwords in text area and toggle its visibility.

        Args:
            kwargs: any parameter from a v.TextField. If set, 'type' will be overwritten.
        """
        # default behavior
        kwargs.setdefault("label", ms.password_field.label)
        kwargs.setdefault("class_", "mr-2")
        kwargs.setdefault("v_model", "")
        kwargs["type"] = "password"
        kwargs.setdefault("append_icon", "fa-solid fa-eye-slash")

        # init the widget with the remaining kwargs
        super().__init__(**kwargs)

        # bind the js behavior
        self.on_event("click:append", self._toggle_pwd)

    def _toggle_pwd(self, *args) -> None:
        """Toggle password visibility when append button is clicked."""
        if self.type == "text":
            self.type = "password"
            self.append_icon = "fa-solid fa-eye-slash"
        else:
            self.type = "text"
            self.append_icon = "fa-solid fa-eye"

        return


class NumberField(v.TextField, SepalWidget):
    max_: t.Int = t.Int(10).tag(sync=True)
    "Maximum selectable number."

    min_: t.Int = t.Int(0).tag(sync=True)
    "Minimum selectable number."

    increm: t.Int = t.Int(1).tag(sync=True)
    "Incremental value added at each step."

    def __init__(self, max_: int = 10, min_: int = 0, increm: int = 1, **kwargs):
        r"""Custom widget to input numbers in text area and add/subtract with single increment.

        Args:
            max\_: Maximum selectable number. Defaults to 10.
            min\_: Minimum selectable number. Defaults to 0.
            increm: incremental value added at each step. default to 1
            kwargs: Any parameter from a v.TextField. If set, 'type' will be overwritten.
        """
        # set the traits
        self.max_ = max_
        self.min_ = min_
        self.increm = increm

        # set default params
        kwargs["type"] = "number"
        kwargs.setdefault("append_outer_icon", "fa-solid fa-plus")
        kwargs.setdefault("prepend_icon", "fa-solid fa-minus")
        kwargs.setdefault("v_model", 0)
        kwargs.setdefault("readonly", True)

        # call the constructor
        super().__init__(**kwargs)

        self.on_event("click:append-outer", self.increment)
        self.on_event("click:prepend", self.decrement)

    def increment(self, *args) -> None:
        """Adds increm to the current v_model number."""
        self.v_model = min((self.v_model + self.increm), self.max_)

        return

    def decrement(self, *args) -> None:
        """Subtracts increm to the current v_model number."""
        self.v_model = max((self.v_model - self.increm), self.min_)

        return


class VectorField(v.Col, SepalWidget):
    original_gdf: Optional[gpd.GeoDataFrame] = None
    "The originally selected dataframe"

    df: Optional[pd.DataFrame] = None
    "the original dataframe without the geometry (for column naming)"

    gdf: Optional[gpd.GeoDataFrame] = None
    "The selected dataframe"

    w_file: Optional[FileInput] = None
    "The file selector widget"

    w_column: Optional[v.Select] = None
    "The Select widget to select the column"

    w_value: Optional[v.Select] = None
    "The Select widget to select the value in the selected column"

    v_model: t.Dict = t.Dict(
        {
            "pathname": None,
            "column": None,
            "value": None,
        }
    )
    "The json saved v_model shaped as {'pathname': xx, 'column': xx, 'value': xx}"

    column_base_items: list = [
        {"text": ms.widgets.vector.all, "value": "ALL"},
        {"divider": True},
    ]
    "the column compulsory selector (ALL)"

    feature_collection: Optional[ee.FeatureCollection] = None
    "ee.FeatureCollection: the selected featureCollection"

    def __init__(self, label: str = ms.widgets.vector.label, gee: bool = False, **kwargs) -> None:
        """A custom input widget to load vector data.

        The user will provide a vector file compatible with fiona or a GEE feature collection.
        The user can then select a specific shape by setting column and value fields.

        Args:
            label: the label of the file input field, default to 'vector file'.
            gee: whether to use GEE assets or local vectors.
            folder: When gee=True, extra args will be used for AssetSelect
            kwargs: any parameter from a v.Col. if set, 'children' will be overwritten.
        """
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

    def reset(self) -> Self:
        """Return the field to its initial state."""
        self.w_file.reset()

        return self

    @sd.switch("loading", on_widgets=["w_column", "w_value"])
    def _update_file(self, change: dict) -> Self:
        """Update the file name, the v_model and reset the other widgets."""
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
            columns = [str(col) for col in columns if col not in ["system:index", "Shape_Area"]]

        # update the columns
        self.w_column.items = self.column_base_items + sorted(set(columns))

        self.w_column.v_model = "ALL"

        return self

    @sd.switch("loading", on_widgets=["w_value"])
    def _update_column(self, change: dict) -> Self:
        """Update the column name and empty the value list."""
        # set the value
        self._set_v_model("column", change["new"])

        # exit if nothing as the only way to set this value to None is the reset
        if not change["new"]:
            return self

        # reset value widget
        self.w_value.items = []
        self.w_value.v_model = ""

        # hide value if "ALL" or none
        if change["new"] in ["ALL", ""]:
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

    def _update_value(self, change: dict) -> Self:
        """Update the value name and reduce the gdf."""
        # set the value
        self._set_v_model("value", change["new"])

        return self

    def _set_v_model(self, key: str, value: Any) -> None:
        """Set the v_model from an external function to trigger the change event.

        Args:
            key: the column name
            value: the new value to set
        """
        tmp = self.v_model.copy()
        tmp[key] = value or None
        self.v_model = tmp

        return


class SimpleSlider(v.Slider, SepalWidget):
    def __init__(self, **kwargs) -> None:
        """Simple Slider is a simplified slider that can be center aligned in table.

        The normal vuetify slider is included html placeholder for the thumbs and the messages (errors and hints). This is preventing anyone from center-aligning them in a table. This class is behaving exactly like a regular Slider but embed extra css class to prevent the display of these sections. any hints or message won't be displayed.
        """
        super().__init__(**kwargs)
        self.class_list.add("v-no-messages")
