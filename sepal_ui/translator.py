import json
from types import SimpleNamespace
from pathlib import Path
from collections import abc


class Translator(SimpleNamespace):
    
    def __init__(self, json_folder, default_lan, target_lan):
        
        super().__init__()
        
        if type(json_folder) == str:
            json_folder = Path(json_folder)
        
        # reading both the default and the language dictionnaire
        default_dict = json.loads(json_folder.joinpath(f'{default_lan}.json').read_text())
        target_dict = json.loads(json_folder.joinpath(f'{target_lan}.json').read_text())

        # create a composite dict replaceing all the default keys with the one availabel in the target lan
        ms_dict = self.update(default_dict, target_dict)
        
        print(ms_dict)
        
        # transform it into a json str
        ms_json = json.dumps(ms_dict)
        
        # unpack the json as a simple namespace
        ms = json.loads(ms_json, object_hook=lambda d: SimpleNamespace(**d))
        
        for k, v in ms.__dict__.items():
            setattr(self, k, getattr(ms, k))
        
        
    def update(self, d, u):
        """update the fallback dictionnaire (d) values with the keys that exist in the target (u) dictionnaire"""
        for k, v in u.items():
            if isinstance(v, abc.Mapping):
                d[k] = self.update(d.get(k, {}), v)
            else:
                d[k] = v
        
        return d
        