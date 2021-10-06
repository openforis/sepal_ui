import pytest

from sepal_ui import sepalwidgets as sw


class TestNumberField:
    def test_init(self, number):

        assert isinstance(number, sw.NumberField)
        assert number.type == "number"
        assert number.max_ == 10
        assert number.min_ == 0

        return

    def test_increment(self, number):

        # increment to 5
        [number.increment(None, None, None) for i in range(5)]
        assert number.v_model == 5

        # init with a max
        number = sw.NumberField(max_=5)
        # increment to 10
        [number.increment(None, None, None) for i in range(10)]
        assert number.v_model == 5

        return

    def test_decrement(self, number):

        # increment to 5
        [number.decrement(None, None, None) for i in range(5)]
        assert number.v_model == 0

        # init with a negative min
        number = sw.NumberField(min_=-5)
        # increment to 10
        [number.decrement(None, None, None) for i in range(2)]
        assert number.v_model == -2

        return

    @pytest.fixture
    def number(self):
        """return a NumberField"""

        return sw.NumberField()
