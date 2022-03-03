import json
from types import SimpleNamespace
from pathlib import Path
from collections import abc
from deepdiff import DeepDiff


class Translator(SimpleNamespace):
    """
    The translator is a SimpleNamespace of Simplenamespace. It reads 2 Json files, the first one being the source language (usually English) and the second one the target language.
    It will replace in the source dictionary every key that exist in both json dictionaries. Following this procedure, every message that is not translated can still be accessed in the source language.
    To access the dictionary keys, instead of using [], you can simply use key name as in an object ex: translator.first_key.secondary_key.
    There are no depth limits, just respect the snake_case convention when naming your keys in the .json files.

    Args:
        json_folder (str | pathlib.Path): The folder where the dictionaries are stored
        target_lan (str): The language code (IETF BCP 47) of the target lang (it should be the same as the target dictionary)
        default_lan (str, optional): The language code (IETF BCP 47) of the source lang. default to "en"(it should be the same as the source dictionary)
        file_pattern (str, optional): The file basename of the dictionary without extention. default to "locale".
    """

    FORBIDDEN_KEYS = ["default_dict", "target_dict", "in", "class"]
    "list(str): list of the forbidden keys, using one of them in a translation dict will throw an error"

    target_dict = {}
    "(dict): the target language dictionary"

    default_dict = {}
    "dict: the source language dictionary"

    keys = None
    "all the keys can be acceced as attributes"

    def __init__(
        self, json_folder, target_lan, default_lan="en", file_pattern="locale"
    ):

        # init the simple namespace
        super().__init__()

        # force cast to path
        json_folder = Path(json_folder)

        # reading the default dict
        source_path = json_folder / default_lan / f"{file_pattern}.json"
        self.default_dict = self.sanitize(json.loads(source_path.read_text()))

        # create a dictionary in the target language
        requested, target_lan = self.find_target(json_folder, target_lan)
        target_lan = target_lan or default_lan
        if requested is False:
            print(
                f'The requested language was not available, the translator will fallback to "{target_lan}"'
            )
        target_path = json_folder / target_lan / f"{file_pattern}.json"
        self.target_dict = self.sanitize(json.loads(target_path.read_text()))

        # create the composite dictionary
        ms_dict = self._update(self.default_dict, self.target_dict)

        # check if forbidden keys are being used
        [self.search_key(ms_dict, k) for k in self.FORBIDDEN_KEYS]

        # transform it into a json str
        ms_json = json.dumps(ms_dict)

        # unpack the json as a simple namespace
        ms = json.loads(ms_json, object_hook=lambda d: SimpleNamespace(**d))

        for k, v in ms.__dict__.items():
            setattr(self, k, getattr(ms, k))

    @staticmethod
    def find_target(folder, target):
        """
        find the target language in the available language folder

        given a folder and a target lang, this function returns the closest language available in the folder
        If nothing is found falling back to any working subvariety and return None if it doesn't exist

        Args:
            folder (pathlib.Path): the folder where the languages dictionnaries are stored
            target (str): the target lang in IETF BCP 47

        Return:
            (bool, str): a bool to tell if the exact requested lan were available and the closest lang in IETF BCP 47
        """

        lang = None

        # first scenario the target is available
        if (folder / target).is_dir():
            lang = target
        # second senario the "main lang" is set
        elif (folder / target[:2]).is_dir():
            lang = target[:2]
        # third scenario we search for any closely related language
        else:
            try:
                f = next(f for f in folder.glob(f"{target[:2]}-*") if f.is_dir())
                lang = f.stem
            except StopIteration:
                pass

        return (lang == target, lang)

    @classmethod
    def search_key(cls, d, key):
        """
        Search a specific key in the d dictionary and raise an error if found

        Args:
            d (dict): the dictionary to study
            key (str): the key to look for
        """

        for k, v in d.items():
            if isinstance(v, abc.Mapping):
                cls.search_key(v, key)
            else:
                if k == key:
                    raise Exception(
                        f"You cannot use the key {key} in your translation dictionary"
                    )

        return

    @classmethod
    def sanitize(cls, d):
        """
        Identify numbered dictionnaries embeded in the dict and transform them into lists

        This function is an helper to prevent deprecation after the introduction of pontoon for translation.
        The user is now force to use keys even for numbered lists. SimpleNamespace doesn't support integer indexing so this function will transform back this "numbered" dictionnary (with integer keys) into lists.

        Args:
            d (dict): the dictionnary to sanitize

        Return:
            (dict): the sanitized dictionnary
        """

        ms = d.copy()

        # create generator based on input type
        if isinstance(ms, dict):
            gen = ms.items()
        elif isinstance(ms, list):
            gen = enumerate(ms)

        # loop into the keys of the dict modify them
        for k, v in gen:
            if isinstance(v, dict):
                tmp = v
                if all([k.isnumeric() for k in tmp]):
                    tmp = list(tmp.values())
                ms[k] = cls.sanitize(tmp)
            else:
                ms[k] = v

        return ms

    def _update(self, d, u):
        """
        Update the fallback dictionnaire (d) values with the keys that exist in the target (u) dictionnaire

        Args:
            d (dict): The fallback dictionary
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
            ddiff = DeepDiff(self.default_dict, self.target_dict)[
                "dictionary_item_removed"
            ]
        except Exception:
            ddiff = ["All messages are translated"]

        return "\n".join(ddiff)
