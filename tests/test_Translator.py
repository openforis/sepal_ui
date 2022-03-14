import pytest
from pathlib import Path
import shutil
import json
from configparser import ConfigParser

from sepal_ui import config_file
from sepal_ui.translator import Translator


class TestTranslator:
    def test_init(self, translation_folder, tmp_config_file):

        # assert that the test key exist in fr
        translator = Translator(translation_folder, "fr")
        assert translator.test_key == "Clef de test"

        # assert that the the code work if the path is a str
        translator = Translator(str(translation_folder), "fr")
        assert translator.test_key == "Clef de test"

        # assert that the test does not exist in es and we fallback to en
        translator = Translator(translation_folder, "es")
        assert translator.test_key == "Test key"

        # assert that using a non existing lang lead to fallback to english
        translator = Translator(translation_folder, "it")
        assert translator.test_key == "Test key"

        # assert that if nothing is set it will use the confi_file (fr-FR)
        translator = Translator(translation_folder)
        assert translator.test_key == "Clef de test"

        return

    def test_search_key(self):

        # assert that having a wrong key in the json will raise an error
        key = "toto"
        d = {"a": {"toto": "b"}, "c": "d"}

        with pytest.raises(Exception):
            Translator.search_key(d, key)

        return

    def test_sanitize(self):

        # a test dict with many embeded numbered list
        # but also an already existing list
        test = {
            "foo1": {"0": "foo2", "1": "foo3"},
            "foo4": {
                "foo5": {"0": "foo6", "1": "foo7"},
                "foo8": "foo9",
            },
            "foo10": ["foo11", "foo12"],
        }

        # the sanitize version of this
        result = {
            "foo1": ["foo2", "foo3"],
            "foo4": {"foo5": ["foo6", "foo7"], "foo8": "foo9"},
            "foo10": ["foo11", "foo12"],
        }

        assert Translator.sanitize(test) == result

        return

    def test_missing_keys(self, translation_folder):

        # check that all keys are in the fr dict
        translator = Translator(translation_folder, "fr")
        assert translator.missing_keys() == "All messages are translated"

        # check that 1 key is missing
        translator = Translator(translation_folder, "es")
        assert translator.missing_keys() == "root['test_key']"

        return

    def test_find_target(self, translation_folder):

        # test grid
        test_grid = {
            "en": ("en", "en"),
            "en-US": ("en-US", "en"),
            "fr-FR": ("fr-FR", "fr-FR"),
            "fr-CA": ("fr-CA", "fr"),
            "fr": ("fr", "fr"),
            "da": ("da", None),
        }

        # loop in the test grid to check multiple language combinations
        for k, v in test_grid.items():
            assert Translator.find_target(translation_folder, k) == v

        return

    def test_available_locales(self, translation_folder):

        # expected grid
        res = ["es", "fr", "fr-FR", "en"]

        # create the translator
        # -en- to -en-
        translator = Translator(translation_folder)

        assert translator.available_locales() == res

        return

    @pytest.fixture(scope="class")
    def translation_folder(self):
        """
        Generate a fully qualified translation folder with limited keys in en, fr and es.
        Cannot use the temfile lib as we need the directory to appear in the tree
        """

        # set up the appropriate keys for each language
        keys = {
            "en": {"a_key": "A key", "test_key": "Test key"},
            "fr": {"a_key": "Une clef", "test_key": "Clef de test"},
            "fr-FR": {"a_key": "Une clef", "test_key": "Clef de test"},
            "es": {"a_key": "Una llave"},
        }

        # generate the tmp_dir in the test directory
        tmp_dir = Path(__file__).parent / "data" / "messages"
        tmp_dir.mkdir(exist_ok=True, parents=True)

        # create the translation files
        for lan, d in keys.items():
            folder = tmp_dir / lan
            folder.mkdir()
            (folder / "locale.json").write_text(json.dumps(d, indent=2))

        yield tmp_dir

        # flush everything
        shutil.rmtree(tmp_dir)

        return

    @pytest.fixture(scope="function")
    def tmp_config_file(self):
        """
        Erase any existing config file and replace it with one specifically
        design for thesting the translation
        """

        # erase anything that exists
        if config_file.is_file():
            config_file.unlink()

        # create a new file
        config = ConfigParser()
        config.add_section("sepal-ui")
        config.set("sepal-ui", "locale", "fr-FR")
        config.write(config_file.open("w"))

        yield 1

        # flush it
        config_file.unlink()

        return
