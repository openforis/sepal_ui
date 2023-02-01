import pytest

from sepal_ui import sepalwidgets as sw


class TestRadioGroup:
    def test_init(self) -> None:

        radios = [sw.Radio(active=None, value=i) for i in range(3)]
        group = sw.RadioGroup(v_model=None, children=radios)

        assert isinstance(group, sw.RadioGroup)

        return

    def test_update_radios(self, group: sw.RadioGroup) -> None:

        group.v_model = 1
        assert group.children[0].active is False
        assert group.children[1].active is True
        assert group.children[2].active is False

        return

    def test_update_v_model(self, group: sw.RadioGroup) -> None:

        group.children[2].active = True
        assert group.v_model == 2
        assert group.children[0].active is False
        assert group.children[1].active is False

        return

    @pytest.fixture
    def group(self) -> sw.RadioGroup:
        """return a Radiogroup with 3 radios children"""

        radios = [sw.Radio(active=None, value=i) for i in range(3)]
        return sw.RadioGroup(v_model=None, children=radios)
