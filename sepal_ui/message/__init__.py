import os
from pathlib import Path

from sepal_ui.translator import Translator

# pick the language
lang = 'en'
if 'CUSTOM_LANGUAGE' in os.environ:
    lang = os.environ['CUSTOM_LANGUAGE']

ms = Translator(Path(__file__).parent, lang)