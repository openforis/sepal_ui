import ipyvuetify as v
from markdown import markdown
from traitlets import Unicode, Any
from ipywidgets import link
from deprecated.sphinx import versionadded

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget

__all__ = ["Markdown", "Tooltip", "CopyToClip"]


class Markdown(v.Layout, SepalWidget):
    """
    Custom Layout based on the markdown text given

    Args:
        mkd_str (str): the text to display using the markdown convention. multi-line string are also interpreted
        kwargs (optional): Any parameter from a v.Layout. If set, 'children' will be overwritten
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

        # set default parameters
        kwargs["row"] = kwargs.pop("row", True)
        kwargs["class_"] = kwargs.pop("class_", "pa-5")
        kwargs["align_center"] = kwargs.pop("align_center", True)
        kwargs["children"] = [v.Flex(xs12=True, children=[content])]

        # call the constructor
        super().__init__(**kwargs)


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
                if name != "_cross_validation_lock":
                    raise RuntimeError(
                        f"You can't modify the attributes of the {self.__class__} after instantiated"
                    )
        super().__setattr__(name, value)


@versionadded(version="2.2.0", reason="New clipping widget")
class CopyToClip(v.VuetifyTemplate):
    """
    Custom textField that provides a handy copy-to-clipboard javascript behaviour.
    When the clipboard btn is clicked the v_model will be copied in the local browser clipboard. You just have to change the clipboard v_model. when copied, the icon change from a copy to a check.

    Args:
        kwargs: any argument that can be used with a v.TextField
    """

    tf = None
    "v.TextField: the textfield widget that holds the v_model to copy"

    v_model = Any(None).tag(sync=True)
    "Any trait: a v_model trait that embed the string to copy"

    def __init__(self, **kwargs):

        # add the default params to kwargs
        kwargs["outlined"] = kwargs.pop("outlined", True)
        kwargs["label"] = kwargs.pop("label", "Copy To clipboard")
        kwargs["readonly"] = kwargs.pop("readonly", True)
        kwargs["append_icon"] = kwargs.pop("append_icon", "mdi-clipboard-outline")
        kwargs["v_model"] = kwargs.pop("v_model", None)
        kwargs["class_"] = kwargs.pop("class_", "ma-5")

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
                    document.execCommand("copy");
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
