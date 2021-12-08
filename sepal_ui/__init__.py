__author__ = """Pierrick Rambaud"""
__email__ = "pierrick.rambaud49@gmail.com"
__version__ = "2.5.3"

# direct access to colors
from sepal_ui.frontend import styles
import ipyvuetify as v
from types import SimpleNamespace

theme = v.theme.themes.dark if v.theme.dark else v.theme.themes.light
"traitlets: the theme used in sepal"

color = SimpleNamespace(
    bg=styles.bg_color,
    primary=theme.primary,
    accent=theme.accent,
    secondary=theme.secondary,
    success=theme.success,
    info=theme.info,
    warning=theme.warning,
    error=theme.error,
)
'SimpleNamespace: the colors of sepal. members are in the following list: "bg, primary, accent, secondary, success, info, warning, error". They will render according to the selected theme.'
