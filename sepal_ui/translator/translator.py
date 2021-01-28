import json
from types import SimpleNamespace
from pathlib import Path
from collections import abc
from deepdiff import DeepDiff


class Translator(SimpleNamespace):
    
    def __init__(self, json_folder, target_lan, default_lan='en'):
        
        super().__init__()
        
        if type(json_folder) == str:
            json_folder = Path(json_folder)
        
        # reading both the default dict
        self.default_dict = json.loads(json_folder.joinpath(f'{default_lan}.json').read_text())
        
        # create a composite dict replaceing all the default keys with the one availabel in the target lan        
        target_path = json_folder.joinpath(f'{target_lan}.json')
        self.target_dict = self.default_dict.copy()
        
        if target_path.is_file():
            self.target_dict = json.loads(target_path.read_text())
        else:
            print(f'No json file is provided for "{target_lan}", fallback to "en"')

        
        ms_dict = self._update(self.default_dict, self.target_dict)
        
        # transform it into a json str
        ms_json = json.dumps(ms_dict)
        
        # unpack the json as a simple namespace
        ms = json.loads(ms_json, object_hook=lambda d: SimpleNamespace(**d))
        
        for k, v in ms.__dict__.items():
            setattr(self, k, getattr(ms, k))
        
        
    def _update(self, d, u):
        """update the fallback dictionnaire (d) values with the keys that exist in the target (u) dictionnaire"""
        
        ms = d.copy()
        
        for k, v in u.items():
            if isinstance(v, abc.Mapping):
                ms[k] = self._update(d.get(k, {}), v)
            else:
                ms[k] = v
        
        return ms
    
    def missing_keys(self):
        """this function is intended for developper use only
           print the list of the missing keys in the target dictionnairie
        """
        
        # find all the missing keys
        try: 
            ddiff = DeepDiff(self.default_dict, self.target_dict)['dictionary_item_removed']
        except:
            ddiff = ['All messages are translated']
        
        return  '\n'.join(ddiff)
        
        