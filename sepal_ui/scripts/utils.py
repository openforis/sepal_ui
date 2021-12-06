import os
from pathlib import Path
from urllib.parse import urlparse
import string
import random
import math
import re
import warnings
from unidecode import unidecode
from functools import wraps
from itertools import product

import ee
from cryptography.fernet import Fernet
from matplotlib import colors as c

import sepal_ui

from .warning import SepalWarning


def hide_component(widget):
    """
    hide a vuetify based component

    Args:
        widget (v.VuetifyWidget): the widget to hide
    """

    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.hide()

    elif "d-none" not in str(widget.class_):
        widget.class_ = str(widget.class_).strip() + " d-none"

    return widget


def show_component(widget):
    """
    show a vuetify based component

    Args:
        widget (v.VuetifyWidget): the widget to hide
    """

    if isinstance(widget, sepal_ui.sepalwidgets.sepalwidget.SepalWidget):
        widget.show()

    elif "d-none" in str(widget.class_):
        widget.class_ = widget.class_.replace("d-none", "")

    return widget


def create_download_link(pathname):
    """
    Create a clickable link to download the pathname target

    Args:
        pathname (str | pathlib.Path): the pathname th download

    Return:
        (str): the download link
    """

    if type(pathname) == str:
        pathname = Path(pathname)

    result_path = Path(pathname).expanduser()
    home_path = Path("~").expanduser()

    # will be available with python 3.9
    # download_path = result_path.relative_to(home_path) if result_path.is_relative_to(home_path) else result_path
    download_path = os.path.relpath(result_path, home_path)

    link = f"/api/files/download?path=/{download_path}"

    return link


def is_absolute(url):
    """
    Check if the given URL is an absolute or relative path

    Args:
        url (str): the URL to test

    Return:
        (bool): True if absolute else False
    """
    return bool(urlparse(str(url)).netloc)


def random_string(string_length=3):
    """
    Generates a random string of fixed length.

    Args:
        string_length (int, optional): Fixed length. Defaults to 3.

    Return:
        (str): A random string
    """

    # random.seed(1001)
    letters = string.ascii_lowercase

    return "".join(random.choice(letters) for i in range(string_length))


def get_file_size(filename):
    """
    Get the file size as string of 2 digit in the adapted scale (B, KB, MB....)

    Args:
        filename (str | pathlib.Path): the path to the file to mesure

    Return:
        (str): the file size in a readable humanly readable
    """

    file_size = Path(filename).stat().st_size

    if file_size == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    i = int(math.floor(math.log(file_size, 1024)))
    s = file_size / (1024 ** i)

    return "{:.1f} {}".format(s, size_name[i])


def init_ee():
    """
    Initialize earth engine according to the environment.
    It will use the creddential file if the EE_PRIVATE_KEY env variable exist.
    Otherwise it use the simple Initialize command (asking the user to register if necessary)
    """

    # only do the initialization if the credential are missing
    if not ee.data._credentials:

        # if the decrypt key is available use the decript key
        if "EE_DECRYPT_KEY" in os.environ:

            # read the key as byte
            key = os.environ["EE_DECRYPT_KEY"].encode()

            # create the fernet object
            fernet = Fernet(key)

            # decrypt the key
            json_encrypted = Path(__file__).parent / "encrypted_key.json"
            with json_encrypted.open("rb") as f:
                json_decripted = fernet.decrypt(f.read()).decode()

            # write it to a file
            with open("ee_private_key.json", "w") as f:
                f.write(json_decripted)

            # connection to the service account
            service_account = "test-sepal-ui@sepal-ui.iam.gserviceaccount.com"
            credentials = ee.ServiceAccountCredentials(
                service_account, "ee_private_key.json"
            )
            ee.Initialize(credentials)

        # if in local env use the local user credential
        else:
            ee.Initialize()

    return


def catch_errors(alert, debug=False):
    """
    Decorator to execute try/except sentence
    and catch errors in the alert message.
    If debug is True then the error is raised anyway

    Params:
        alert (sw.Alert): Alert to display errors
        debug (bool): Wether to raise the error or not, default to false
    """

    def decorator_alert_error(func):
        @wraps(func)
        def wrapper_alert_error(*args, **kwargs):
            value = None
            try:
                value = func(*args, **kwargs)
            except Exception as e:
                alert.add_msg(f"{e}", type_="error")
                if debug:
                    raise e
            return value

        return wrapper_alert_error

    return decorator_alert_error


def need_ee(func):
    """
    Decorator to execute check if the object require EE binding.
    Trigger an exception if the connection is not possible.

    Params:
        func (obj): the object on which the decorator is applied
    """

    @wraps(func)
    def wrapper_ee(*args, **kwargs):

        # try to connect to ee
        try:
            init_ee()
        except Exception:
            raise Exception("This function needs an Earth Engine authentication")

        return func(*args, **kwargs)

    return wrapper_ee


def loading_button(alert=None, button=None, debug=False):
    """
    Decorator to execute try/except sentence and toggle loading button object.
    Designed to work within the Tile object, or any object that have a self.btn and self.alert set.

    Params:
        button (sw.Btn, optional): Toggled button
        alert (sw.Alert, optional): the alert to display the error message
        debug (bool, optional): wether or not the exception should stop the execution. default to False
    """

    def decorator_loading(func):
        @wraps(func)
        def wrapper_loading(self, *args, **kwargs):

            # set btn and alert
            # Change name of variable to assign it again in this scope
            button_ = self.btn if not button else button
            alert_ = self.alert if not alert else alert

            # Clean previous loaded messages in alert
            alert_.reset()

            button_.toggle_loading()  # Start loading
            value = None
            try:
                # Catch warnings in the process function
                with warnings.catch_warnings(record=True) as w_list:
                    value = func(self, *args, **kwargs)

                # Check if there are warnings in the function and append them
                # Use append msg as several warnings could be triggered
                if w_list:

                    # split the warning list
                    w_list_sepal = [
                        w for w in w_list if isinstance(w.message, SepalWarning)
                    ]

                    # display the sepal one
                    ms_list = [
                        f"{w.category.__name__}: {w.message.args[0]}"
                        for w in w_list_sepal
                    ]
                    [alert_.append_msg(ms, type_="warning") for ms in ms_list]

                    # only display them in the console if debug mode
                    if debug:

                        def custom_showwarning(w):
                            return warnings.showwarning(
                                message=w.message,
                                category=w.category,
                                filename=w.filename,
                                lineno=w.lineno,
                                line=w.line,
                            )

                        [custom_showwarning(w) for w in w_list]

            except Exception as e:
                alert_.add_msg(f"{e}", "error")
                if debug:
                    button_.toggle_loading()  # Stop loading button if there is an error
                    raise e

            button_.toggle_loading()  # Stop loading button

            return value

        return wrapper_loading

    return decorator_loading


def normalize_str(msg, folder=True):
    """
    Normalize an str to make it compatible with file naming (no spaces, special chars ...etc)

    Params:
        msg (str): the string to sanitise
        folder (optional|bool): if the name will be used for folder naming or for display. if display, <'> and < > characters will be kept

    Return:
        (str): the modified str
    """

    regex = "[^a-zA-Z\d\-\_]" if folder else "[^a-zA-Z\d\-\_\ ']"

    return re.sub(regex, "_", unidecode(msg))


def to_colors(in_color, out_type="hex"):
    """
    Transform any color type into a color in the specified output format
    avalable format: hex

    Args:
        in_color (str or tuple): It can be a string (e.g., 'red', '#ffff00', 'ffff00') or RGB tuple (e.g., (255, 127, 0)).
        out_type (str, optional): the type of the output color from ['hex']. default to 'hex'

    Returns:
        (str|tuple): The color in the specified format. default to black.
    """

    # list of the color function used for the translatio
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


def switch(*params, debug=True, on_widgets=[], targets=[]):
    """
    Decorator to switch the state of input boolean parameters on class widgets or the
    class itself. If on_widgets is defined, it will switch the state of every widget
    parameter, otherwise it will change the state of the class (self). You can also set
    two decorators on the same function, one could affect the class and other the widgets.

    Args:
        *params (str): any boolean parameter of a SepalWidget.
        debug (bool): Whether trigger or not an Exception if the decorated function fails.
        on_widgets (list(widget_names,)|optional): List of widget names into the class
        targets (list(bool,)|optional); list of the target value (value taht will be set on switch. default to the inverse of the current state.

    """

    def decorator_switch(func):
        @wraps(func)
        def wrapper_switch(self, *args, **kwargs):

            widgets_len = len(on_widgets)
            targets_len = len(targets)

            # sanity check on targets and on_widgets
            if widgets_len and targets_len:
                if widgets_len != targets_len:
                    raise IndexError(
                        f'the length of "on_widgets" ({widgets_len}) is different from the length of "targets" ({targets_len})'
                    )

            # create the list of target values based on the target list
            # or the initial values of the widgets params
            # The first one is taken as reference
            if not targets_len:
                w = getattr(self, on_widgets[0]) if widgets_len else self
                targets_ = [bool(getattr(w, p)) for p in params]
            else:
                targets_ = targets

            if widgets_len:

                # Verify that the input elements are strings
                wrong_types = [
                    (w, type(w)) for w in on_widgets if not isinstance(w, str)
                ]

                if len(wrong_types):
                    errors = [
                        f"Received:{w_type} for widget: {w}."
                        for w, w_type in wrong_types
                    ]

                    raise TypeError(
                        f"All on_widgets list elements has to be strings. [{' '.join(errors)}]"
                    )

                missing_widgets = [w for w in on_widgets if not hasattr(self, w)]

                if missing_widgets:
                    raise Exception(
                        f"The provided {missing_widgets} widget(s) does not exist in the current class"
                    )

                def w_assign(bool_targets):

                    params_targets = [
                        (p, bool_targets[i]) for i, p in enumerate(params)
                    ]

                    for (w_name, p_t) in product(on_widgets, params_targets):
                        param, target = p_t
                        widget = getattr(self, w_name)
                        setattr(widget, param, target)

            else:

                def w_assign(bool_targets):
                    for i, p in enumerate(params):
                        setattr(self, p, bool_targets[i])

            # assgn the parameters to the target inverse
            w_assign([not t for t in targets_])

            # execute the function and catch errors
            try:
                func(self, *args, **kwargs)

            except Exception as e:
                if debug:
                    w_assign(targets_)
                    raise e

            # reassign the parameters to the targets
            w_assign(targets_)

        return wrapper_switch

    return decorator_switch


def next_string(string):
    """Create a string followed by an underscore and a consecutive number"""

    # if the string is already numbered the last digit is separeted from the rest of the string by an "_"
    split = string.split("_")
    end = split[-1]

    if end.isdigit():
        string = "_".join(split[:-1]) + f"_{int(end)+1}"
    else:
        string += "_1"

    return string
