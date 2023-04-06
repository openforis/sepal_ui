"""All the helper function of sepal-ui."""

import math
import os
import random
import re
import string
import warnings
from pathlib import Path
from typing import Any, Sequence, Union
from urllib.parse import urlparse

import ee
import httplib2
import ipyvuetify as v
from anyascii import anyascii
from deprecated.sphinx import deprecated, versionadded
from matplotlib import colors as c

import sepal_ui
from sepal_ui.conf import config, config_file
from sepal_ui.message import ms
from sepal_ui.scripts import decorator as sd
from sepal_ui.scripts.warning import SepalWarning


def hide_component(widget: v.VuetifyWidget) -> v.VuetifyWidget:
    """Hide a vuetify based component.

    Args:
        widget: the widget to hide

    Returns:
        the widget
    """
    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.hide()

    elif "d-none" not in str(widget.class_):
        widget.class_ = str(widget.class_).strip() + " d-none"

    return widget


def show_component(widget: v.VuetifyWidget) -> v.VuetifyWidget:
    """Show a vuetify based component.

    Args:
        widget: the widget to hide

    Returns:
        the widget
    """
    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.show()

    elif "d-none" in str(widget.class_):
        widget.class_ = widget.class_.replace("d-none", "")

    return widget


def create_download_link(pathname: Union[str, Path]) -> str:
    """Create a clickable link to download the pathname target.

    Args:
        pathname: the pathname th download

    Returns:
        the download link
    """
    # return the link if it's an absolute url
    if isinstance(pathname, str) and bool(urlparse(str(pathname)).netloc):
        return pathname

    # create a downloadable link from the jupyter node
    pathname = Path(pathname)
    try:
        download_path = pathname.relative_to(Path.home())
    except ValueError:
        download_path = pathname

    # I want to use the ipyurl lib to guess the url of the Jupyter server on the fly
    # but I don't really understand how it works
    # so here is an ugly fix only compatible with SEPAL
    link = f"https://sepal.io/api/sandbox/jupyter/files/{download_path}"

    return link


def random_string(string_length: int = 3) -> str:
    """Generates a random string of fixed length.

    Args:
        string_length: Fixed length. Defaults to 3.

    Returns:
        A random string
    """
    letters = string.ascii_lowercase

    return "".join(random.choice(letters) for i in range(string_length))


def get_file_size(filename: Union[str, Path]) -> str:
    """Get the file size as string of 2 digit in the adapted scale (B, KB, MB....).

    Args:
        filename: the path to the file to mesure

    Returns:
        the file size in a readable humanly readable
    """
    file_size = Path(filename).stat().st_size

    if file_size == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    i = int(math.floor(math.log(file_size, 1024)))
    s = file_size / (1024**i)

    return "{:.1f} {}".format(s, size_name[i])


def init_ee() -> None:
    """Initialize earth engine according to the environment.

    It will use the creddential file if the EARTHENGINE_TOKEN env variable exist.
    Otherwise it use the simple Initialize command (asking the user to register if necessary).
    """
    # only do the initialization if the credential are missing
    if not ee.data._credentials:

        # if the credentials token is asved in the environment use it
        if "EARTHENGINE_TOKEN" in os.environ:

            # write the token to the appropriate folder
            ee_token = os.environ["EARTHENGINE_TOKEN"]
            credential_folder_path = Path.home() / ".config" / "earthengine"
            credential_folder_path.mkdir(parents=True, exist_ok=True)
            credential_file_path = credential_folder_path / "credentials"
            credential_file_path.write_text(ee_token)

        # if the user is in local development the authentication should
        # already be available
        ee.Initialize(http_transport=httplib2.Http())

    return


def normalize_str(msg: str, folder: bool = True) -> str:
    """Normalize an str to make it compatible with file naming (no spaces, special chars ...etc).

    Params:
        msg: the string to sanitise
        folder: if the name will be used for folder naming or for display. if display, <'> and < > characters will be kept

    Returns:
        the modified str
    """
    regex = "[^a-zA-Z\d\-\_]" if folder else "[^a-zA-Z\d\-\_\ ']"

    return re.sub(regex, "_", anyascii(msg))


def to_colors(
    in_color: Union[str, Sequence], out_type: str = "hex"
) -> Union[str, tuple]:
    """Transform any color type into a color in the specified output format.

    Avalable format: [hex]

    Args:
        in_color: It can be a string (e.g., 'red', '#ffff00', 'ffff00') or RGB tuple (e.g., (255, 127, 0)).
        out_type: the type of the output color from ['hex']. default to 'hex'

    Returns:
        The color in the specified format. default to black.
    """
    # list of the color function used for the translation
    c_func = {"hex": c.to_hex}
    transform = c_func[out_type]

    out_color = "#000000"  # default black color

    if isinstance(in_color, tuple) and len(in_color) == 3:

        # rescale color if necessary
        if all(isinstance(item, int) for item in in_color):
            in_color = [c / 255.0 for c in in_color]

        return transform(in_color)

    else:

        # try to guess the color system
        try:
            return transform(in_color)
        except Exception:
            pass

        # try again by adding an extra # (GEE handle hex codes without #)
        try:
            return transform(f"#{in_color}")
        except Exception:
            pass

    return transform(out_color)


def next_string(string: str) -> str:
    """Create a string followed by an underscore and a consecutive number.

    Args:
        string: the initial string

    Returns:
        the incremented string
    """
    # if the string is already numbered the last digit is separeted from the rest of the string by an "_"
    split = string.split("_")
    end = split[-1]

    if end.isdigit():
        string = "_".join(split[:-1]) + f"_{int(end)+1}"
    else:
        string += "_1"

    return string


def set_config(key: str, value: str, section: str = "sepal-ui") -> None:
    """Set a config variable.

    Set the provided value to the given key for the given section in the sepal-ui config
    file.

    Args:
        key: key configuration name
        value: value to be referenced by the configuration key
        section: configuration section, defaults to sepal-ui.
    """
    # set the section if needed
    if "sepal-ui" not in config.sections():
        config.add_section(section)

    # set the value
    config.set("sepal-ui", key, value)

    # save back the file
    config.write(config_file.open("w"))

    return


@deprecated(
    version="2.9.1", reason="This function will be removed in favor of set_config()"
)
def set_config_locale(locale: str) -> None:
    """Set the provided local in the sepal-ui config file.

    Args:
        locale: a locale name in IETF BCP 47 (no verifications are performed)
    """
    return set_config("locale", locale)


@deprecated(
    version="2.9.1", reason="This function will be removed in favor of set_config()"
)
def set_config_theme(theme: str) -> None:
    """Set the provided theme in the sepal-ui config file.

    Args:
        theme: a theme name (currently supporting "dark" and "light")
    """
    return set_config("theme", theme)


@versionadded(version="2.7.1")
def set_type(color: str) -> str:
    r"""Return a pre-defined material colors based on the requested type\_ parameter.

    If the parameter is not a predifined color, fallback to "info" and will raise a warning. the colors can only be selected from ["primary", "secondary", "accent", "error", "info", "success", "warning", "anchor"].

    Args:
        color: the requested color

    Returns:
        a pre-defined material color

    """
    from sepal_ui.frontend.styles import TYPES

    if color not in TYPES:
        warnings.warn(
            f'the selected color "{color}" is not a pre-defined material color. It should be one from [{", ".join(TYPES)}]',
            SepalWarning,
        )
        color = TYPES[0]

    return color


@versionadded(version="2.8.0")
def geojson_to_ee(
    geo_json: dict, geodesic: bool = False, encoding: str = "utf-8"
) -> ee.FeatureCollection:
    """Transform a geojson object into a featureCollection or a Geometry.

    No sanity check is performed on the initial geo_json. It must respect the
    `__geo_interface__ <https://gist.github.com/sgillies/2217756>`__.

    Args:
        geo_json: a geo_json dictionnary
        geodesic: Whether line segments should be interpreted as spherical geodesics. If false, indicates that line segments should be interpreted as planar lines in the specified CRS. If absent, defaults to True if the CRS is geographic (including the default EPSG:4326), or to False if the CRS is projected. Defaults to False.
        encoding: The encoding of characters. Defaults to "utf-8".

    Returns:
        the created featurecollection
    """
    # from a featureCollection
    if geo_json["type"] == "FeatureCollection":
        for feature in geo_json["features"]:
            if feature["geometry"]["type"] != "Point":
                feature["geometry"]["geodesic"] = geodesic
        features = ee.FeatureCollection(geo_json)
        return features

    # from a single feature
    elif geo_json["type"] == "Feature":
        geom = None
        # Checks whether it is a point
        if geo_json["geometry"]["type"] == "Point":
            coordinates = geo_json["geometry"]["coordinates"]
            longitude = coordinates[0]
            latitude = coordinates[1]
            geom = ee.Geometry.Point(longitude, latitude)
        # for every other geometry simply create a geometry
        else:
            geom = ee.Geometry(geo_json["geometry"], "", geodesic)

        return geom

    # some error handling because we are fancy
    else:
        raise ValueError("Could not convert the geojson to ee.Geometry()")

    return


def check_input(input_: Any, msg: str = ms.utils.check_input.error) -> bool:
    r"""Check if the inpupt value is initialized.

    If not raise an error, else return True.

    Args:
        input\_: the input to check
        msg: the message to display if the input is not set

    Return:
        check if the value is initialized
    """
    # by the default the variable is considered valid
    init = True

    # check the collection type that are the only one supporting the len method
    try:
        init = False if len(input_) == 0 else init
    except Exception:
        init = False if input_ is None else init

    if init is False:
        raise ValueError(msg)

    return init


################################################################################
# the soon to be deprecated decorators
#

# fmt: off
catch_errors = deprecated(version='3.0', reason="use sepal_ui.scripts.decorator.catch_errors instead")(sd.catch_errors)
need_ee = deprecated(version='3.0', reason="use sepal_ui.scripts.decorator.need_ee instead")(sd.need_ee)
loading_button = deprecated(version='3.0', reason="use sepal_ui.scripts.decorator.need_ee instead")(sd.loading_button)
switch = deprecated(version='3.0', reason="use sepal_ui.scripts.decorator.switch instead")(sd.switch)
# fmt: on
