"""Test the FileInput widget in pysepal.sepalwidgets.file_input."""

from pathlib import Path

from pysepal.sepalwidgets.file_input import FileInput


def test_select_file_accepts_path(tmp_path: Path) -> None:
    """select_file must accept a Path and store string traits.

    current_folder is a Unicode trait, so assigning a Path raised a TraitError.
    """
    csv = tmp_path / "classes.csv"
    csv.write_text("lc_class,desc,color\n1,a,#000000\n")

    file_input = FileInput(initial_folder=str(tmp_path), root=str(tmp_path))
    file_input.select_file(csv)

    assert file_input.value == str(csv)
    assert file_input.current_folder == str(tmp_path)


def test_select_file_accepts_str(tmp_path: Path) -> None:
    """select_file must also accept a plain string path (str has no .parent)."""
    csv = tmp_path / "classes.csv"
    csv.write_text("lc_class,desc,color\n1,a,#000000\n")

    file_input = FileInput(initial_folder=str(tmp_path), root=str(tmp_path))
    file_input.select_file(str(csv))

    assert file_input.value == str(csv)
    assert file_input.current_folder == str(tmp_path)
