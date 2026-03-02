"""Application model for the Solara map application template.

This module defines the AppModel class that stores application state and configuration.
"""
from sepal_ui.model import Model
from traitlets import Unicode


class AppModel(Model):
    """Model class for the map application.

    Stores application-specific data and configuration including the app name.
    """

    app_name = Unicode("Map Application").tag(sync=True)

    def __init__(self):
        """Initialize the AppModel with default values."""
        super().__init__()
