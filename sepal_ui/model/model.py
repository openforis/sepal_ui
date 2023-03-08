"""Abstract object to store information in your application.

Helper methods can be used to share information between tiles and/or save them
"""

import json
from typing import Union

import ipyvuetify as v
from ipywidgets import dlink
from traitlets import HasTraits
from typing_extensions import Self

__all__ = ["Model"]


class Model(HasTraits):
    """Model object to store information of your computation (input, output.. etc).

    The Model structure is based on traitlets and embed function for export or import in json format. The model traitlets can be bind to any widget field.
    """

    def __repr__(self) -> str:
        """Method to represent the Model objects as a string."""
        data = [f"{k}={val}" for k, val in self.export_data().items()]
        args = ", ".join(data).strip()

        return f"{self.__class__.__name__}({args})"

    def export_data(self) -> dict:
        """Export a json description of all the object traitlets.

        Note that the members will be ignored.

        Returns:
            the serialized traitlets
        """
        return self.__dict__["_trait_values"]

    def import_data(self, data: Union[dict, str]) -> None:
        """Import the model (i.e. the traitlets) from a json file.

        Args:
            data: the json ditionary of the model
        """
        # cast to a json dict
        json_data = json.loads(data) if isinstance(data, str) else data

        for k, val in json_data.items():
            getattr(self, k)  # to raise an error if the json is malformed
            setattr(self, k, val)

        return

    def bind(self, widget: v.VuetifyWidget, trait: str) -> Self:
        """Binding a widget input 'v_model' trait to a trait of the model.

        The binding will be unidirectionnal for the sake of some custom widget that does not support it.
        This wrapper avoid to import the ipywidgets lib everywhere and reduce the number of parameters
        Some existence check are also performed and will throw an error if the trait doesn't exist.

        Args:
            widget: any input widget with a v_model trait
            trait: the name of a trait of the current model
        """
        # check trait existence
        getattr(self, trait)

        # bind them
        dlink((widget, "v_model"), (self, trait))

        # maybe I would add the possiblity to add an alert to display stuff to the user with the same options as in alert.bind

        return self
