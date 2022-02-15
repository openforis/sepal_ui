import pytest
from pathlib import Path
import io
from contextlib import redirect_stdout
import shutil
import json

from sepal_ui.translator import Translator


class TestTranslator:
    def test_init(self, translation_folder):

        # assert that the test key exist in fr
        translator = Translator(translation_folder, "fr")
        assert translator.test_key == "Clef de test"

        # assert that the the code work if the path is a str
        translator = Translator(str(translation_folder), "fr")
        assert translator.test_key == "Clef de test"

        # assert that the test does not exist in es and we fallback to en
        translator = Translator(translation_folder, "es")
        assert translator.test_key == "Test key"

        # assert that using a non existing lang lead to a warning
        f = io.StringIO()
        with redirect_stdout(f):
            translator = Translator(translation_folder, "it")
        assert f.getvalue() == 'No json file is provided for "it", fallback to "en"\n'

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

    @pytest.fixture(scope="class")
    def translation_folder(self):
        """
        Generate a fully qualified translation folder with limited keys in en, fr and spanish.
        Cannot use the temfile lib as we need the directory to appear in the tree
        """

        # set up the appropriate keys for each language
        keys = {
            "en": {"a_key": "A key", "test_key": "Test key"},
            "fr": {"a_key": "Une clef", "test_key": "Clef de test"},
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
