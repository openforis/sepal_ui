import pytest
from sepal_ui import sepalwidgets as sw
from sepal_ui.model import Model
from traitlets import Any


class TestFileInput:
    def test_init(self, root_dir):

        # default init
        file_input = sw.FileInput()

        assert isinstance(file_input, sw.FileInput)
        assert file_input.v_model is None

        # init with a string
        file_input = sw.FileInput(folder=str(root_dir))

        assert isinstance(file_input, sw.FileInput)
        assert file_input.v_model is None

        # get all the names
        assert "sepal_ui" in self.get_names(file_input)

        # default init
        file_input = sw.FileInput([".rst"], folder=root_dir)

        assert "LICENSE" not in self.get_names(file_input)
        assert "AUTHORS.rst" in self.get_names(file_input)

        return

    def test_bind(self, file_input):
        class Test_io(Model):
            out = Any(None).tag(sync=True)

        test_io = Test_io()

        test_io.bind(file_input, "out")

        path = "toto.ici.shp"
        file_input.v_model = path

        assert test_io.out == path
        assert file_input.file_menu.v_model is False

        return

    def test_on_file_select(self, root_dir, file_input, readme):

        file_input._on_file_select({"new": root_dir})

        assert file_input.v_model is None
        assert "README.rst" in self.get_names(file_input)

        # select readme
        file_input._on_file_select({"new": readme})
        assert file_input.v_model in str(readme)

        # check that select is not changed if nothing is provided
        file_input._on_file_select({"new": None})
        assert file_input.v_model in str(readme)

        return

    def test_on_reload(self, file_input, tmp_dir):

        # move to the tmp directory
        file_input._on_file_select({"new": tmp_dir})

        # assert that the file does not exist
        name = "text.txt"

        assert name not in self.get_names(file_input)

        # create the file and reload the widget
        tmp_file = tmp_dir / name
        tmp_file.write_text("a test \n")
        file_input._on_reload(None, None, None)

        assert name in self.get_names(file_input)

        # delete the file
        tmp_file.unlink()

        return

    def test_reset(self, file_input, root_dir, readme):

        # move into sepal_ui folders
        file_input.select_file(readme)

        file_input.reset()

        # assert that the folder has been reset
        assert file_input.v_model is None
        assert file_input.folder != str(root_dir)

        return

    def test_select_file(self, file_input, readme):

        # move into sepal_ui folders
        file_input.select_file(readme)

        # assert that the file has been selected
        assert file_input.v_model == str(readme)

        # assert exeption if path is not a file
        with pytest.raises(Exception):
            file_input.select_file(readme.parent)

        return

    @pytest.fixture
    def file_input(self, root_dir):
        """create a default file_input in the root_dir"""

        return sw.FileInput(folder=root_dir)

    @staticmethod
    def get_names(widget):
        """get the list name of a fileinput object"""

        name_list = []
        for item_list in widget.file_list.children[0].children:
            name_list.append(item_list.children[1].children[0].children[0])

        return name_list
