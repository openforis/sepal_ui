import pytest
from pathlib import Path
import io
from contextlib import redirect_stdout

from sepal_ui.translator import Translator


class TestTranslator:
    def test_init(self):

        # assert that the test key exist in fr
        target_lan = "fr"
        translator = Translator(self._get_message_json_folder(), target_lan)

        assert translator.test_key == "Clef de test"

        # assert that the the code work if the path is a str
        target_lan = "fr"
        translator = Translator(str(self._get_message_json_folder()), target_lan)
        assert translator.test_key == "Clef de test"

        # assert that the test does not exist in es and we fallback to en
        target_lan = "es"

        translator = Translator(self._get_message_json_folder(), target_lan)
        assert translator.test_key == "Test key"

        # assert that using a non existing lang lead to a warning
        target_lan = "it"
        f = io.StringIO()
        with redirect_stdout(f):
            translator = Translator(self._get_message_json_folder(), target_lan)
        assert f.getvalue() == 'No json file is provided for "it", fallback to "en"\n'

        return

    def test_search_key(self):

        # assert that having a wrong key in the json will raise an error
        key = "toto"
        d = {"a": {"toto": "b"}, "c": "d"}

        with pytest.raises(Exception):
            Translator.search_key(d, key)

        return

    def _get_message_json_folder(self):

        # use the json folder of the lib
        home = Path(__file__).parent.parent.absolute()
        path = home / "sepal_ui" / "message"

        return path
