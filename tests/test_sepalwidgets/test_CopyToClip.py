import pytest

from sepal_ui import sepalwidgets as sw


class TestClip:
    def test_init(self):

        # minimal clip
        clip = sw.CopyToClip()
        assert clip.tf.outlined is True
        assert isinstance(clip.tf.label, str)
        assert clip.tf.append_icon == "fa-solid fa-clipboard"
        assert clip.tf.v_model == ""

        # clip with extra options
        clip = sw.CopyToClip(outlined=False, dense=True)
        assert clip.tf.outlined is False
        assert clip.tf.dense is True

        return

    def test_copy(self, clip):

        clip.tf.fire_event("click:append", None)

        # I don't know how to check the clipboard

        # check the icon change
        assert clip.tf.append_icon == "fa-solid fa-clipboard-check"

        return

    def test_change(self, clip):

        # test value
        test_value = "tot"

        # change the widget value
        clip = sw.CopyToClip()
        clip.v_model = test_value

        # check
        assert clip.tf.v_model == test_value

        return

    @pytest.fixture
    def clip(self):
        """create a simple clip-to-clipboard with a v_model set to "value"."""
        return sw.CopyToClip(v_model="value")
