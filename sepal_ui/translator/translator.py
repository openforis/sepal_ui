import json
from types import SimpleNamespace
from pathlib import Path
from collections import abc
from deepdiff import DeepDiff


class Translator(SimpleNamespace):
    """
    The translator is a SimpleNamespace of Simplenamespace. It read 2 json file, the first one being the source language (usually english) and the second one the target language. 
    It will replace in the source dict every key that exist in both json dict. Following this procedure, every message that is not translated can still be accessed in the source language. 
    To access the dict keys, instead of using [], you can simply use key name as in an object ex: translator.first_key.secondary_key. 
    There are no depth limits, just respect the snake_case convention when naming your keys in the .json dicts.
    
    Args: 
        json_folder (str | pathlib.Path): the folder where the dictionnaries are stored
        target_lan (str): the language code of the target lang (it should be the same as the target dictionnary)
        default_lan (str): the language code of the source lang (it should be the same as the source dictionnary)
        
    Attributes:
        default_dict (dict): the source language dictionnary
        target_dict (dict): the target language dictionnary 
        (keys): all the keys can be acceced as attributes. make sure to never use default_dict and target_dict
    
    """
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

        
        # create the composite dictionnary
        ms_dict = self._update(self.default_dict, self.target_dict)
        
        # verify if 'default_dict' or 'target_dict' is in use
        self.search_key(ms_dict, 'default_dict')
        self.search_key(ms_dict, 'target_dict')
        
        # transform it into a json str
        ms_json = json.dumps(ms_dict)
        
        # unpack the json as a simple namespace
        ms = json.loads(ms_json, object_hook=lambda d: SimpleNamespace(**d))
        
        for k, v in ms.__dict__.items():
            setattr(self, k, getattr(ms, k))
    
    @classmethod
    def search_key(cls, d, key):
        """
        Search a specific key in the d dictionnary and raise an error if found
        
        Args:
            d (dict): the dictionnary to study 
            key (str): the key to look for
        """
        
        for k, v in d.items():
            if isinstance(v, abc.Mapping):
                cls.search_key(v, key)
            else:
                if k == key:
                    raise Exception(f"You cannot use the key {key} in your translation dictionnary")
                    break
        
        return None
        
    def _update(self, d, u):
        """ 
        Update the fallback dictionnaire (d) values with the keys that exist in the target (u) dictionnaire
        
        Args:
            d (dict): The fallback dictionnary
            u (dict): the target dctionnary
            
        Return:
            ms (dict): The updated dictionnay
        """
        
        ms = d.copy()
        
        for k, v in u.items():
            if isinstance(v, abc.Mapping):
                ms[k] = self._update(d.get(k, {}), v)
            else:
                ms[k] = v
        
        return ms
    
    def missing_keys(self):
        """
        this function is intended for developer use only
        print the list of the missing keys in the target dictionnairie
        
        Return:
            (str): the list of missing keys
        """
        
        # find all the missing keys
        try: 
            ddiff = DeepDiff(self.default_dict, self.target_dict)['dictionary_item_removed']
        except:
            ddiff = ['All messages are translated']
        
        return  '\n'.join(ddiff)
        
        