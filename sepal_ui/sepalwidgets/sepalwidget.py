from ipyvue import VueWidget
import ipyvuetify as v
from traitlets import Unicode, Bool, observe
from deprecated.sphinx import versionadded

__all__ = ["SepalWidget", "Tooltip"]


class SepalWidget(v.VuetifyWidget):
    """
    Custom vuetifyWidget to add specific methods

    Args:
        viz (bool, optional): define if the widget should be visible or not
        tooltip (str, optional): tooltip text of the widget. If set the widget will be displayed on :code:`self.widget` (irreversible).
    """

    viz = Bool(True).tag(sync=True)
    "Bool: whether the widget is displayed or not"

    old_class = Unicode("").tag(sync=True)
    "Unicode: a saving attribute of the widget class"

    with_tooltip = None
    "sw.ToolTip: the full widget and its tooltip. Useful for display purposes when a tooltip has been set"

    def __init__(self, viz=True, tooltip=None, **kwargs):

        # init the widget
        super().__init__(**kwargs)

        # setup the viz status
        self.viz = viz

        # create a tooltip only if a message is set
        self.set_tooltip(tooltip)

    @observe("viz")
    def _set_viz(self, change):
        """
        hide or show the component according to its viz param value.

        Hide the widget by reducing the html class to :code:`d-none`.
        Show the widget by removing the :code:`d-none` html class.
        Save the previous class

        Args:
            change: the dict of a trait callback
        """

        # will be replaced byt direct calls to built-in hide
        # once the previous custom implementation will be fully removed

        if self.viz:

            # change class value
            self.class_ = self.old_class or self.class_
            self.class_list.remove("d-none")

        else:

            # change class value
            self.class_list.remove("d-none")
            self.old_class = str(self.class_)
            self.class_ = "d-none"

        return

    def toggle_viz(self):
        """
        toogle the visibility of the widget.

        Return:
            self
        """

        self.viz = not self.viz

        return self

    def hide(self):
        """
        Hide the widget by reducing the html class to :code:`d-none`.
        Save the previous class and set viz attribute to False.

        Return:
            self
        """

        # update viz state
        self.viz = False

        return self

    def show(self):
        """
        Show the widget by removing the d-none html class.
        Save the previous class and set viz attribute to True.

        Return:
            self
        """

        # update viz state
        self.viz = True

        return self

    def reset(self):
        """
        Clear the widget v_model. Need to be extented in custom widgets to fit the structure of the actual input.

        Return:
            self
        """

        self.v_model = None

        return self

    def get_children(self, id_):
        """Retrieve all children elements that matches with the given id_.

        Args:
            id_ (str, optional): attribute id to compare with.

        Returns:
            Will return a list with all mathing elements if there are more than one,
            otherwise will return the mathing element.

        """

        elements = []

        def search_children(parent):

            if issubclass(parent.__class__, VueWidget):

                if parent.attributes.get("id") == id_:
                    elements.append(parent)

                if len(parent.children):
                    [search_children(chld) for chld in parent.children]

        # Search in the self children elements
        [search_children(chld) for chld in self.children]

        return elements[0] if len(elements) == 1 else elements

    def set_children(self, children, position="first"):
        """Insert input children in self children within given position

        Args:
            children (str, DOMWidget, list(str, DOMWidget)):
            position (str): whether to insert as first or last element. ["first", "last"]
        """

        if not isinstance(children, list):
            children = [children]

        new_childrens = self.children[:]

        if position == "first":
            new_childrens = children + new_childrens

        elif position == "last":
            new_childrens = new_childrens + children

        else:
            raise ValueError(
                f"Position '{position}' is not a valid value. Use 'first' or 'last'"
            )

        self.children = new_childrens

        return self

    @versionadded(version="2.9.0", reason="Tooltip are now integrated to widgets")
    def set_tooltip(self, txt=None, **kwargs):
        """
        Create a tooltip associated with the widget. If the text is not set, the
        tooltip will be automatically removed. Once the tooltip is set the object
        variable can be accessed normally but to render the widget, one will need
        to use :code:`self.with_tooltip` (irreversible).

        Args:
            txt (str): anything False (0, False, empty text, None) will lead to the removal of the tooltip. everything else will be used to fill the text area
            kwargs: any options available in a Tooltip widget

        Returns:
            (sw.Tooltip): the tooltip associated with the object
        """
        if isinstance(self.with_tooltip, Tooltip):
            self.with_tooltip.children = [txt]
            self.with_tooltip.disabled = not bool(txt)
        elif bool(txt) is True:
            self.with_tooltip = Tooltip(self, txt, **kwargs)

        return self


class Tooltip(v.Tooltip):
    """
    Custom widget to display tooltip when mouse is over widget

    Args:
        widget (Vuetify.widget): widget used to display tooltip
        tooltip (str): the text to display in the tooltip
    """

    def __init__(self, widget, tooltip, **kwargs):

        # set some default parameters
        kwargs["close_delay"] = kwargs.pop("close_delay", 200)

        self.v_slots = [
            {"name": "activator", "variable": "tooltip", "children": widget}
        ]
        widget.v_on = "tooltip.on"

        self.children = [tooltip]

        super().__init__(**kwargs)
