"""Locale-aware translator for the demo app.

The other templates build a module-level ``Translator`` at import time, which
pins the app to one language for the life of the process. A Solara app has one
locale per connection, so the translator has to be built per render instead:
``use_locale`` reads the connection's resolved code and re-renders when the
user picks a new language in the app bar.

Accessed via ``from component.message import use_translator``.
"""

from pathlib import Path

import solara

from pysepal.solara import use_locale
from pysepal.translator import Translator

MESSAGE_DIR = Path(__file__).parent


def use_translator() -> Translator:
    """Return a Translator following this connection's resolved locale.

    Returns:
        A Translator rebuilt whenever the locale changes.
    """
    locale = use_locale()
    return solara.use_memo(lambda: Translator(MESSAGE_DIR, target=locale), [locale])
