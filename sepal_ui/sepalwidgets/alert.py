from datetime import datetime

from ipywidgets import jslink
import ipyvuetify as v
from traitlets import Unicode, observe, directional_link, Bool

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget
from sepal_ui.scripts.utils import set_type
from sepal_ui.frontend.styles import TYPES
from sepal_ui.message import ms

__all__ = ["Divider", "Alert", "StateBar", "Banner"]


class Divider(v.Divider, SepalWidget):
    """
    A custom Divider with the ability to dynamically change color
    Whenever the type\_ trait is modified, the divider class will change accordingly

    Args:
        class\_ (str, optional): the initial color of the divider
        kwargs (optional): any parameter from a v.Divider. if set, 'class\_' will be overwritten.
    """

    type_ = Unicode("").tag(sync=True)
    "str: Added type\_ trait to specify the current color of the divider"

    def __init__(self, class_="", **kwargs):
        kwargs["class_"] = class_
        super().__init__(**kwargs)

    @observe("type_")
    def add_class_type(self, change):
        """
        Change the color of the divider according to the type\_
        It is binded to the type\_ traitlet but can also be called manually

        Args:
            change (dict): the only useful key is 'new' which is the new required color

        Return:
            self
        """

        self.class_list.remove(*TYPES)
        self.class_list.add(change["new"])

        return self


class Alert(v.Alert, SepalWidget):
    """
    A custom Alert widget. It is used as the output of all processes in the framework.
    In the voila interfaces, print statement will not be displayed.
    Instead use the sw.Alert method to provide information to the user.
    It's hidden by default.

    Args:
        type\_ (str, optional): The color of the Alert
        kwargs (optional): any parameter from a v.Alert. If set, 'type' will be overwritten.
    """

    def __init__(self, type_="info", **kwargs):

        # set default parameters
        kwargs["text"] = kwargs.pop("text", True)
        kwargs["type"] = set_type(type_)
        kwargs["class_"] = kwargs.pop("class_", "mt-5")

        # call the constructor
        super().__init__(**kwargs)

        self.hide()

    def update_progress(self, progress, msg="Progress", bar_length=30):
        """
        Update the Alert message with a progress bar. This function will stay until we manage to use tqdm in the widgets

        Args:
            progress (float): the progress status in float [0, 1]
            msg (str, optionnal): The message to use before the progress bar
            bar_length (int, optionnal): the length of the progress bar in characters

        Return:
            self
        """

        # define the characters to use in the progress bar
        plain_char = "█"
        empty_char = " "

        # cast the progress to float
        progress = float(progress)
        if not (0 <= progress <= 1):
            raise ValueError(f"progress should be in [0, 1], {progress} given")

        # set the length parameter
        block = int(round(bar_length * progress))

        # construct the message content
        text = f"|{plain_char * block + empty_char * (bar_length - block)}|"

        # add the message to the output
        self.add_live_msg(
            v.Html(
                tag="span",
                children=[
                    v.Html(tag="span", children=[f"{msg}: "], class_="d-inline"),
                    v.Html(tag="pre", class_="info--text d-inline", children=[text]),
                    v.Html(
                        tag="span",
                        children=[f" {progress *100:.1f}%"],
                        class_="d-inline",
                    ),
                ],
            )
        )

        return self

    def add_msg(self, msg, type_="info"):
        """
        Add a message in the alert by replacing all the existing one.
        The color can also be changed dynamically

        Args:
            msg (str): the message to display
            type\_ (str, optional): the color to use in the widget

        Return:
            self
        """
        self.show()
        self.type = set_type(type_)
        self.children = [v.Html(tag="p", children=[msg])]

        return self

    def add_live_msg(self, msg, type_="info"):
        """
        Add a message in the alert by replacing all the existing one.
        Also add the timestamp of the display.
        The color can also be changed dynamically

        Args:
            msg (str): the message to display
            type\_ (str, optional): the color to use in the widget

        Return:
            self
        """

        current_time = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

        self.show()
        self.type = set_type(type_)
        self.children = [
            v.Html(tag="p", children=["[{}]".format(current_time)]),
            v.Html(tag="p", children=[msg]),
        ]

        return self

    def append_msg(self, msg, section=False, type_="info"):
        """
        Append a message in a new parragraph, with or without divider

        Args:
            msg (str): the message to display
            section (bool, optional): add a Divider before the added message

        Return:
            self
        """

        self.show()
        self.type = type_

        if len(self.children):
            current_children = self.children[:]
            if section:
                # As the list is mutable, and the trait is only triggered when
                # the children is changed, so have to create a copy.
                divider = Divider(class_="my-4", style="opacity: 0.22")

                # link Alert type with divider type
                directional_link((self, "type"), (divider, "type_"))
                current_children.extend([divider, v.Html(tag="p", children=[msg])])
                self.children = current_children

            else:
                current_children.append(v.Html(tag="p", children=[msg]))
                self.children = current_children
        else:
            self.add_msg(msg)

        return self

    def remove_last_msg(self):
        """
        Remove the last msg printed in the Alert widget

        Return:
            self
        """

        if len(self.children) > 1:
            current_children = self.children[:]
            self.children = current_children[:-1]
        else:
            self.reset()

        return self

    def reset(self):
        """
        Empty the messages and hide it

        Return:
            self
        """

        self.children = [""]
        self.hide()

        return self

    def check_input(self, input_, msg=None):
        """
        Check if the inpupt value is initialized.
        If not return false and display an error message else return True

        Args:
            input\_ (any): the input to check
            msg (str, optionnal): the message to display if the input is not set

        Return:
            (bool): check if the value is initialized
        """
        if not msg:
            msg = "The value has not been initialized"
        init = True

        # check the collection type that are the only one supporting the len method
        try:
            init = False if len(input_) == 0 else init
        except Exception:
            init = False if input_ is None else init

        if init is False:
            self.add_msg(msg, "error")

        return init


class StateBar(v.SystemBar):

    """Widget to display quick messages on simple inline status bar

    Args:
       kwargs (optional): any parameter from a v.SystemBar. If set, 'children' will be overwritten.
    """

    msg = Unicode("").tag(sync=True)
    "str: the displayed message"

    loading = Bool(False).tag(sync=True)
    "bool: either or not the circular progress is spinning"

    progress = None
    "widget: The ProgressCircular widget that will be displayed in the statebar"

    def __init__(self, **kwargs):

        self.progress = v.ProgressCircular(
            indeterminate=self.loading,
            value=100,
            small=True,
            size=15,
            color="primary",
            class_="mr-2",
        )

        # set default parameter
        kwargs["children"] = [self.progress, self.msg]

        # call the constructor
        super().__init__(**kwargs)

        jslink((self, "loading"), (self.progress, "indeterminate"))

    @observe("loading")
    def _change_loading(self, change):
        """Change progress wheel state"""
        self.progress.indeterminate = self.loading

    @observe("msg")
    def _change_msg(self, change):
        """Change state bar message"""
        self.children = [self.progress, self.msg]

    def add_msg(self, msg, loading=False):
        """Change current status message"""
        self.msg = msg
        self.loading = loading

        return self


class Banner(v.Snackbar, SepalWidget):
    """
    Custom Snackbar widget to display messages as a banner in module App.

    Args:
       msg (str, optional): Message to display in application banner. default to nothing
       type\_ (str, optional): Used to display an appropiate banner color. fallback to "info".
       id_ (str, optional): unique banner identificator.
       persistent (bool, optional): Whether to close automatically based on the lenght of message (False) or make it indefinitely open (True). Overridden if timeout duration is set.
       kwargs (optional): any parameter from a v.Alert. If set, 'vertical' and 'top' will be overwritten.
    """

    btn_close = None
    "v.Btn: the closing btn of the banner"

    def __init__(self, msg="", type_="info", id_=None, persistent=True, **kwargs):

        # compute the type and default to "info" if it's not existing
        type_ = set_type(type_)

        # create the closing btn
        self.btn_close = v.Btn(
            small=True, text=True, children=[ms.widgets.banner.close]
        )

        # compute timeout based on the persistent and timeout parameter
        computed_timeout = 0 if persistent is True else self.get_timeout(msg)

        kwargs["color"] = kwargs.pop("color", type_)
        kwargs["transition"] = kwargs.pop("transition", "scroll-x-transition")
        kwargs["attributes"] = {"id": id_}
        kwargs["v_model"] = kwargs.pop("v_model", True)
        kwargs["timeout"] = kwargs.pop("timeout", False) or computed_timeout
        kwargs["top"] = True
        kwargs["vertical"] = True
        kwargs["children"] = [msg] + [self.btn_close]
        kwargs["class_"] = "mb-1"

        super().__init__(**kwargs)

        self.btn_close.on_event("click", self.close)

    def close(self, *args):
        """Close button event to close snackbar alert"""
        self.v_model = False

        return

    def get_timeout(self, text):
        """
        Calculate timeout in miliseconds to read the message

        Args:
            text (str): the text displayed in the banner to adapt the duration of the timeout

        Returns
            (int): the duration of the timeout in milliseconds
        """

        wpm = 180  # readable words per minute
        word_length = 5  # standardized number of chars in calculable word
        words = len(text) / word_length
        words_time = ((words / wpm) * 60) * 1000

        delay = 1500  # milliseconds before user starts reading the notification
        bonus = 1000  # extra time

        return delay + words_time + bonus

    def set_btn(self, nb_banner):
        """
        Change the btn display to inform the user on the number of banners in the queue

        Args:
            nb_banner (int): the number of banners in the queue
        """
        msg = ms.widgets.banner
        txt = msg.close if nb_banner == 0 else msg.next.format(nb_banner)
        self.btn_close.children = [txt]

        return
