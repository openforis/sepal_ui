"""MapApp Solara layout package.

Re-exports the public component and its typed prop models.
"""

from .map_app import MapAppComponent, embed_widget
from .models import (
    ExternalLink,
    PanelSection,
    RightPanelAction,
    RightPanelConfig,
    StepAction,
    StepConfig,
)

__all__ = [
    "embed_widget",
    "ExternalLink",
    "MapAppComponent",
    "PanelSection",
    "RightPanelAction",
    "RightPanelConfig",
    "StepAction",
    "StepConfig",
]
