import os
import json
from types import SimpleNamespace
from pathlib import Path

# pick the language
lang = 'en'
if 'CUSTOM_LANGUAGE' in os.environ:
    lang = os.eviron['CUSTOM_LANGUAGE']

# Parse JSON into an object with attributes corresponding to dict keys.
path = Path(__file__).parent.joinpath(f'{lang}.json')

json_file = path.read_text()
ms = json.loads(json_file, object_hook=lambda d: SimpleNamespace(**d))