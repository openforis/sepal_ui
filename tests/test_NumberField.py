import unittest

from sepal_ui import sepalwidgets as sw


class TestNumberField(unittest.TestCase):
    def test_init(self):

        # default init
        number = sw.NumberField()

        self.assertIsInstance(number, sw.NumberField)
        self.assertEqual(number.type, "number")
        self.assertEqual(number.max_, 10)
        self.assertEqual(number.min_, 0)

        return

    def test_increment(self):

        # default init
        number = sw.NumberField()

        # increment to 5
        [number.increment(None, None, None) for i in range(5)]
        self.assertEqual(number.v_model, 5)

        # init with a max
        number = sw.NumberField(max_=5)
        # increment to 10
        [number.increment(None, None, None) for i in range(10)]
        self.assertEqual(number.v_model, 5)

        return

    def test_decrement(self):

        # default init
        number = sw.NumberField()

        # increment to 5
        [number.decrement(None, None, None) for i in range(5)]
        self.assertEqual(number.v_model, 0)

        # init with a negative min
        number = sw.NumberField(min_=-5)
        # increment to 10
        [number.decrement(None, None, None) for i in range(2)]
        self.assertEqual(number.v_model, -2)

        return


if __name__ == "__main__":
    unittest.main()
