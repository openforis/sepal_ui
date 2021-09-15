from pathlib import Path
import pytest

from sepal_ui import sepalwidgets as sw


class TestFileInput:
    def test_init(self):

        # default init
        file_input = sw.FileInput(folder=self._get_sepal_parent())

        # init with a string
        file_input = sw.FileInput(folder=str(self._get_sepal_parent()))

        assert isinstance(file_input, sw.FileInput)
        assert file_input.v_model == ""

        # get all the names
        list_names = []
        for list_item in file_input.file_list.children[0].children:
            list_item_content = list_item.children[1]
            list_item_title = list_item_content.children[0]
            list_names.append(list_item_title.children[0])

        assert "sepal_ui" in list_names

        # default init
        file_input = sw.FileInput([".shp"], folder=self._get_sepal_parent())

        return

    def test_bind(self):

        file_input = sw.FileInput()

        class Test_io:
            def __init__(self):
                self.out = None

        test_io = Test_io()

        output = sw.Alert()
        output.bind(file_input, test_io, "out")

        path = "toto.ici.shp"
        file_input.v_model = path

        assert test_io.out == path
        assert output.viz == True

        return

    def test_on_file_select(self):

        sepal_ui = self._get_sepal_parent()
        file_input = sw.FileInput(folder=sepal_ui)

        # move into sepal_ui folders
        readme = sepal_ui / "README.rst"

        file_input._on_file_select({"new": sepal_ui})

        # get all the names
        list_names = []
        for list_item in file_input.file_list.children[0].children:
            list_item_content = list_item.children[1]
            list_item_title = list_item_content.children[0]
            list_names.append(list_item_title.children[0])

        assert file_input.v_model == ""
        assert "README.rst" in list_names

        # select readme
        file_input._on_file_select({"new": readme})
        assert file_input.v_model in str(readme)

        # check that select is not changed if nothing is provided
        file_input._on_file_select({"new": None})
        assert file_input.v_model in str(readme)

        return

    def test_on_reload(self):

        home = Path.home()
        file_input = sw.FileInput(folder=home)

        # create a fake file
        test_name = "test.txt"
        tmp_file = home / test_name
        tmp_file.write_text("a test \n")

        # reload the folder
        file_input._on_reload(None, None, None)

        # check that the new file is in the list
        list_names = []
        for list_item in file_input.file_list.children[0].children:
            list_item_content = list_item.children[1]
            list_item_title = list_item_content.children[0]
            list_names.append(list_item_title.children[0])

        assert test_name in list_names

        # remove the test file
        tmp_file.unlink()

        return

    def test_reset(self):

        sepal_ui = self._get_sepal_parent()
        file_input = sw.FileInput(folder=sepal_ui)

        # move into sepal_ui folders
        readme = sepal_ui / "README.rst"
        file_input.select_file(readme)

        file_input.reset()

        # assert that the folder has been reset
        assert file_input.v_model == ""
        assert file_input.folder != str(sepal_ui)

        return

    def test_select_file(self):

        sepal_ui = self._get_sepal_parent()
        file_input = sw.FileInput()

        # move into sepal_ui folders
        readme = sepal_ui / "README.rst"

        file_input.select_file(readme)

        # assert that the file has been selected
        assert file_input.v_model == str(readme)

        # assert exeption if path is not a file
        with pytest.raises(Exception):
            file_input.select_file(readme.parent)

        return

    def _get_sepal_parent(self):

        return Path(__file__).parent.parent.absolute()
