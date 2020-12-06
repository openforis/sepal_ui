import os
import json
from types import SimpleNamespace
from pathlib import Path
from collections import abc

def update(d, u):
    for k, v in u.items():
        if isinstance(v, abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

# pick the language
lang = 'en'
if 'CUSTOM_LANGUAGE' in os.environ:
    lang = os.environ['CUSTOM_LANGUAGE']

# Parse JSON into an object with attributes corresponding to dict keys.
# Parse en has a fallback
en_dict = json.loads(Path(__file__).parent.joinpath('en.json').read_text())
lang_dict = json.loads(Path(__file__).parent.joinpath(f'{lang}.json').read_text())

ms_dict = update(en_dict, lang_dict)
ms_json = json.dumps(ms_dict)

ms = json.loads(ms_json, object_hook=lambda d: SimpleNamespace(**d))