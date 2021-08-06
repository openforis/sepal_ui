import unittest

from sepal_ui import sepalwidgets as sw


class TestDatePicker(unittest.TestCase):
    def test_init(self):

        # default init
        datepicker = sw.DatePicker()
        self.assertIsInstance(datepicker, sw.DatePicker)

        # exhaustive
        datepicker = sw.DatePicker("toto")
        self.assertIsInstance(datepicker, sw.DatePicker)

        return

    def test_bind(self):

        datepicker = sw.DatePicker()

        class Test_io:
            def __init__(self):
                self.out = None

        test_io = Test_io()

        output = sw.Alert()
        output.bind(datepicker, test_io, "out")

        date = "2020-06-12"
        datepicker.v_model = date

        self.assertEqual(test_io.out, date)
        self.assertTrue(output.viz)

        return


if __name__ == "__main__":
    unittest.main()
