"""Test the Translator object."""

import json
from configparser import ConfigParser
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from sepal_ui.conf import config_file
from sepal_ui.message import ms
from sepal_ui.translator import Translator


def test_init(translation_folder: Path, tmp_config_file: Path) -> None:
    """Check the Translator can be inited.

    Args:
        translation_folder: the folder where the language keys are stored
        tmp_config_file: create the config file for the prefered language
    """
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

    # check the internal variables once to make sure that they are not removed/changed
    assert translator._folder == str(translation_folder)
    assert translator._default == "en"
    assert translator._targeted == "fr-FR"
    assert translator._target == "fr-FR"
    assert translator._match is True

    # Check that is failing when using

    return


def test_search_key() -> None:
    """Check that a key can be searched in the bbuild messages."""
    # assert that having a wrong key  at root level
    # in the json will raise an error
    key = "toto"
    d = {"toto": {"a": "b"}, "c": "d"}

    with pytest.raises(Exception):
        Translator.search_key(d, key)

    # Search when the key is in a deeper nested level
    key = "nested_key"
    d = {"en": {"level1": {"level2": {"nested_key": "value"}}}}

    with pytest.raises(Exception):
        Translator.search_key(d, key)

    return


def test_sanitize() -> None:
    """Check that the dict are sanitized by the Translator object."""
    # a test dict with many embeded numbered list
    # but also an already existing list
    test = {
        "a": {"0": "b", "1": "c"},
        "d": {"e": {"0": "f", "1": "g"}, "h": "i"},
        "j": ["k", "l"],
    }

    # the sanitize version of this
    result = {
        "a": ["b", "c"],
        "d": {"e": ["f", "g"], "h": "i"},
        "j": ["k", "l"],
    }

    assert Translator.sanitize(test) == result

    return


def test_delete_empty() -> None:
    """Check the translator remove empty keys."""
    test = {"a": "", "b": 1, "c": {"d": ""}, "e": {"f": "", "g": 2}}
    result = {"b": 1, "c": {}, "e": {"g": 2}}

    assert Translator.delete_empty(test) == result

    return


def test_find_target(translation_folder: Path) -> None:
    """Check the targets is found in the folder list and understand ISO 2 codes.

    Args:
        translation_folder: the folder where the language keys are stored
    """
    # test grid
    test_grid = {
        "en": ("en", "en"),
        "en-US": ("en-US", "en"),
        "fr-FR": ("fr-FR", "fr-FR"),
        "fr-CA": ("fr-CA", "fr"),
        "fr": ("fr", "fr"),
        "da": ("da", ""),
    }

    # loop in the test grid to check multiple language combinations
    for k, v in test_grid.items():
        assert Translator.find_target(translation_folder, k) == v

    return


def test_available_locales(translation_folder: Path) -> None:
    """Check the locales are correctly parsed from the existing files.

    Args:
        translation_folder: the folder where the language keys are stored
    """
    # expected grid
    res = ["es", "fr", "fr-FR", "en"]

    # create the translator
    # -en- to -en-
    translator = Translator(translation_folder)

    for locale in res:
        assert locale in translator.available_locales()

    # Check no hidden and protected files are in locales
    locales = translator.available_locales()
    assert not all([(loc.startswith(".") or loc.startswith("_")) for loc in locales])

    return


def test_key_use() -> None:
    """Check that are used at least once."""
    # check key usage method
    # don't test if all keys are translated, crowdin will monitor it
    lib_folder = Path(__file__).parents[1] / "sepal_ui"

    assert "test_key" in ms.key_use(lib_folder, "ms")

    return


@pytest.fixture(scope="module")
def translation_folder() -> Path:
    """Generate a fully qualified translation folder with limited keys in en, fr and es."""
    # set up the appropriate keys for each language
    keys = {
        "en": {"a_key": "A key", "test_key": "Test key"},
        "fr": {"a_key": "Une clef", "test_key": "Clef de test"},
        "fr-FR": {"a_key": "Une clef", "test_key": "Clef de test"},
        "es": {"a_key": "Una llave"},
    }

    with TemporaryDirectory() as tmp_dir:

        # create the translation files
        tmp_dir = Path(tmp_dir)
        for lan, d in keys.items():
            folder = tmp_dir / lan
            folder.mkdir()
            (folder / "locale.json").write_text(json.dumps(d, indent=2))

        yield tmp_dir

    return


@pytest.fixture(scope="module")
def tmp_config_file() -> int:
    """Erase any existing config file and replace it with one specifically design for thesting the translation."""
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
