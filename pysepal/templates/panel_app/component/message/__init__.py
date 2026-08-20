"""Creation of the Translator object associated with the application.

Can be accessed via the foolowing code: ``from component.message import cm``
"""

from pathlib import Path

from pysepal.translator import Translator

# Explicit target on purpose: an untargeted Translator resolves to English.
cm = Translator(Path(__file__).parent, target="en")
