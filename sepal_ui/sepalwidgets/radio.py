"""Add extra behavior to radio and radio group to allow radio to be used as stand_alone components.

The radio from ipyvuetify cannot be used as stand alone elements like checkboxes (https://github.com/vuetifyjs/vuetify/issues/2345). Here the radio included in a radio group will have a v_model trait embedding the active status of the button. In short it's an overlay to reflect the JS into the Python code.
"""

import ipyvuetify as v
from traitlets import Bool, observe

from sepal_ui.sepalwidgets.sepalwidget import SepalWidget

__all__ = ["Radio", "RadioGroup"]


class Radio(v.Radio, SepalWidget):
    """Radio with extra active property."""

    active: Bool = Bool(allow_none=True).tag(sync=True)
    "True when active, False when not"


class RadioGroup(v.RadioGroup, SepalWidget):
    """This class will change the active of the included radio according to its v_model and vice-versa."""

    @observe("children")
    def link_radios(self, *args) -> None:
        """Link all the radio children to the v_model."""
        for w in self.get_children(klass=Radio):
            w.observe(self.update_v_model, "active")

    def update_v_model(self, change: dict) -> None:
        """If a widget value is changed to True, update the v_model of the radioGroup."""
        if change["new"] is True:
            self.v_model = change["owner"].value

        return

    @observe("v_model")
    def update_radios(self, *args) -> None:
        """Update radios v_model.

        Change the v_model of every subsequent radios buttons according to new value of the radioGroup.
        children that are not Radios will be ignored.
        """
        for w in self.get_children(klass=Radio):
            w.active = w.value == self.v_model

        return
