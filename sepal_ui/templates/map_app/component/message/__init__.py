"""Creation of the Translator object associated with the application.

Can be accessed via the foolowing code: ``from component.message import cm``
"""

from pathlib import Path

from sepal_ui.translator import Translator

# create a translator object
cm = Translator(Path(__file__).parent)
