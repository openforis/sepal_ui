import ipyvuetify as v

from sepal_ui import sepalwidgets as sw


class TestClip:
    def test_init(self):

        # minimal clip
        clip = sw.CopyToClip()
        assert clip.tf.outlined == True
        assert isinstance(clip.tf.label, str)
        assert clip.tf.append_icon == "mdi-clipboard-outline"
        assert clip.tf.v_model == None

        # clip with extra options
        clip = sw.CopyToClip(outlined=False, dense=True)
        assert clip.tf.outlined == False
        assert clip.tf.dense == True

        return

    def test_copy(self):

        clip = sw.CopyToClip(v_model="value")
        clip.tf.fire_event("click:append", None)

        # I don't know how to check the clipboard

        # check the icon change
        assert clip.tf.append_icon == "mdi-check"

        return

    def test_change(self):

        # test value
        test_value = "toto"

        # change the widget value
        clip = sw.CopyToClip()
        clip.v_model = test_value

        # check
        assert clip.tf.v_model == test_value

        return
