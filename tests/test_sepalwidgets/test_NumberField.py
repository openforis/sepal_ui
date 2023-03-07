"""Test the NumberField widget"""


from sepal_ui import sepalwidgets as sw


def test_init() -> None:
    """Test Init widget"""

    number = sw.NumberField()

    assert isinstance(number, sw.NumberField)
    assert number.type == "number"
    assert number.max_ == 10
    assert number.min_ == 0
    assert number.increm == 1

    number = sw.NumberField(max_=100, min_=20, increm=10)
    assert number.max_ == 100
    assert number.min_ == 20
    assert number.increm == 10

    return


def test_increment() -> None:
    """Check increment the widget values"""

    number = sw.NumberField()

    # increment to 5
    [number.increment(None, None, None) for i in range(5)]
    assert number.v_model == 5

    # init with a max
    number = sw.NumberField(max_=5)
    # increment to 10
    [number.increment(None, None, None) for i in range(10)]
    assert number.v_model == 5

    # increm with a different step
    number = sw.NumberField(increm=2)
    number.increment(None, None, None)
    assert number.v_model == 2

    return


def test_decrement() -> None:
    """Check decrement the widget values"""

    number = sw.NumberField()

    # increment to 5
    [number.decrement(None, None, None) for i in range(5)]
    assert number.v_model == 0

    # init with a negative min
    number = sw.NumberField(min_=-5)
    # increment to 10
    [number.decrement(None, None, None) for i in range(2)]
    assert number.v_model == -2

    # increm with a different step
    number = sw.NumberField(increm=2, min_=-10)
    number.decrement(None, None, None)
    assert number.v_model == -2

    return
