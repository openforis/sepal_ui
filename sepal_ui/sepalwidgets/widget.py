import ipyvuetify as v
from markdown import markdown
from traitlets import Unicode, Any, observe, dlink
from ipywidgets import link
from deprecated.sphinx import versionadded

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget, Tooltip
from sepal_ui import color

__all__ = ["Markdown", "CopyToClip", "StateIcon"]


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
        kwargs["append_icon"] = kwargs.pop("append_icon", "fas fa-clipboard")
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
        self.tf.append_icon = "fas fa-clipboard-check"

        return


class StateIcon(Tooltip):
    """
    Custom icon with multiple state colors.

    Args:
        model (sepal_ui.Model): Model to manage StateIcon behaviour from outside.
        model_trait (str): Name of trait to be linked with state icon. Must exists in model.
        states (dict): Dictionary where keys are the state name to be linked with self value and value represented by a tuple of two elements. {"key":(tooltip_msg, color)}.
        kwargs: Any arguments from a v.Tooltip
    """

    value = Any().tag(sync=True)
    "bool, str, int: key name of the current state of component. Values must be same as states_dict keys."

    states = None
    'dict: Dictionary where keys are the state name to be linked with self value and value represented by a tuple of two elements. {"key":(tooltip_msg, color)}.'

    icon = None
    "v.Icon: the colored Icon of the tooltip"

    def __init__(self, model, model_trait, states=None, **kwargs):

        # set the default parameter of the tooltip
        kwargs["right"] = kwargs.pop("right", True)

        # init the states
        default_states = {
            "valid": ("Valid", color.success),
            "non_valid": ("Not valid", color.error),
        }
        self.states = default_states if not states else states

        # Get the first value (states first key) to use as default one
        init_value = self.states[next(iter(self.states))]

        self.icon = v.Icon(children=["fas fa-circle"], color=init_value[1], small=True)

        super().__init__(self.icon, init_value[0], **kwargs)

        # Directional from there to link here.
        dlink((model, model_trait), (self, "value"))

    @observe("value")
    def _swap(self, change):
        """Swap between states"""

        new_val = change["new"]

        if not new_val:
            # Use the first value when there is not initial value.
            self.value = next(iter(self.states))
            return

        # Perform a little check with comprehensive error message
        if new_val not in self.states:
            raise ValueError(
                f"Value '{new_val}' is not a valid value. Use {list(self.states.keys())}"
            )
        self.icon.color = self.states[new_val][1]
        self.children = [self.states[new_val][0]]

        return
