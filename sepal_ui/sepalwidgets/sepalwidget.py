import ipyvuetify as v
from markdown import markdown
from traitlets import Unicode

__all__ = ["TYPES", "SepalWidget", "Markdown", "Tooltip"]

TYPES = ("info", "secondary", "primary", "error", "warning", "success", "accent")


class SepalWidget(v.VuetifyWidget):
    """
    Custom vuetifyWidget to add specific methods

    Attributes:
        viz (bool): weather the file is displayed or not
        old_class (str): a saving attribute of the widget class
    """

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.viz = True
        self.old_class = ""

    def toggle_viz(self):
        """
        toogle the visibility of the widget

        Return:
            self
        """

        return self.hide() if self.viz else self.show()

    def hide(self):
        """
        Hide the widget by adding the d-none html class to the widget.
        Save the previous class and set viz attribute to False.

        Return:
            self
        """

        if not "d-none" in str(self.class_):
            self.old_class = self.class_
            self.class_ = "d-none"

        self.viz = False

        return self

    def show(self):
        """
        Hide the widget by removing the d-none html class to the widget
        Save the previous class and set viz attribute to True.

        Return:
            self
        """

        if self.old_class:
            self.class_ = self.old_class

        if "d-none" in str(self.class_):
            self.class_ = str(self.class_).replace("d-none", "")

        self.viz = True

        return self

    def reset(self):
        """
        Clear the widget v_model. Need to be extented in custom widgets to fit the structure of the actual input

        Return:
            self
        """

        self.v_model = None

        return self


class Markdown(v.Layout, SepalWidget):
    """
    Custom Layout based on the markdown text given

    Args:
        mkd_str (str): the text to display using the markdown convention. multi-line string are also interpreted
    """

    def __init__(self, mkd_str="", **kwargs):

        mkd = markdown(mkd_str, extensions=["fenced_code", "sane_lists"])

        # need to be nested in a div to be displayed
        mkd = "<div>\n" + mkd + "\n</div>"

        # make every link to point to target black (to avoid nested iframe in sepal)
        mkd = mkd.replace("<a", '<a target="_blank"')

        # create a Html widget
        class MyHTML(v.VuetifyTemplate):
            template = Unicode(mkd).tag(sync=True)

        content = MyHTML()

        super().__init__(
            row=True,
            class_="pa-5",
            align_center=True,
            children=[v.Flex(xs12=True, children=[content])],
            **kwargs,
        )


class Tooltip(v.Tooltip):
    """
    Custom widget to display tooltip when mouse is over widget

    Args:
        widget (Vuetify.widget): widget used to display tooltip
        tooltip (str): the text to display in the tooltip
    """

    def __init__(self, widget, tooltip, *args, **kwargs):

        self.v_slots = [
            {"name": "activator", "variable": "tooltip", "children": widget}
        ]
        widget.v_on = "tooltip.on"

        self.children = [tooltip]

        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        """prevent set attributes after instantiate tooltip class"""

        if hasattr(self, "_model_id"):
            if self._model_id:
                raise RuntimeError(
                    f"You can't modify the attributes of the {self.__class__} after instantiated"
                )
        super().__setattr__(name, value)


import ipyvuetify as v
from traitlets import Any
from ipywidgets import link


class Clip(v.VuetifyTemplate):
    """
    Custom textField that provides a handy copy-to-clipboard javascript behaviour.
    When the clipboard btn is clicked the v_model will be copied in the local browser clipboard. You just have to change the clipboard v_model. when copied, the icon change from a copy to a check.

    Args:
        kwargs: any argument that can be used with a v.TextField

    Attributes:
        tf (v.TextField): the textfield widget that holds the v_model to copy
        v_model (Any trait): a v_model trait that embed the string to copy
    """

    v_model = Any(None).tag(sync=True)

    def __init__(self, **kwargs):

        # add the default params to kwargs
        if "outlined" not in kwargs:
            kwargs["outlined"] = True
        if "label" not in kwargs:
            kwargs["label"] = "Copy to clipboard"
        if "readonly" not in kwargs:
            kwargs["readonly"] = True
        if "append_icon" not in kwargs:
            kwargs["append_icon"] = "mdi-clipboard-outline"
        if "v_model" not in kwargs:
            kwargs["v_model"] = None

        # set the default v_model
        self.v_model = kwargs["v_model"]

        # create component
        self.tf = v.TextField(**kwargs)
        self.components = {"mytf": self.tf}

        # template with js behaviour
        self.template = """
        <mytf/>
        <script> 
            {methods: {
                jupyter_clip(_txt) {
                    var tempInput = document.createElement("input");
                    tempInput.value = _txt;
                    document.body.appendChild(tempInput);
                    tempInput.focus();
                    tempInput.select();
                    alert(document.execCommand("copy"));
                    document.body.removeChild(tempInput); 
                }
            }}
        </script>"""

        super().__init__()

        # js behaviour
        self.tf.on_event("click:append", self._clip)
        link((self, "v_model"), (self.tf, "v_model"))

    def _clip(self, widget, event, data):
        self.send({"method": "clip", "args": [self.tf.v_model]})
        self.tf.append_icon = "mdi-check"
