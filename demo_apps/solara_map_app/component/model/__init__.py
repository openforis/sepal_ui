"""Model components for the Solara map application.

This package contains the data models used by the map application template.
"""

from .legend import LayerLegend
from .model import AppModel
from .processing import ProcessingOutputs

__all__ = ["AppModel", "LayerLegend", "ProcessingOutputs"]
