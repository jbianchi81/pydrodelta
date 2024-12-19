from unittest import TestCase
from pandas import DataFrame, date_range, Timestamp, NA, notnull
from pydrodelta.util import extrapolate_linear

class Test_LinearExtrapolate(TestCase):

    def test_run(self):
        data = DataFrame({
            "date": date_range(start=Timestamp(2000,1,1), periods=10, freq='D'),
            "valor": [0, 0.5, 1, 1.5, 2, NA, NA, NA, NA, NA]
        })

        # set index
        data.set_index("date", inplace=True)

        result = extrapolate_linear(
            data = data, column = "valor", 
            extrapolation_limit = 3, 
            train_length = 5)
        

        self.assertEqual(len(result[notnull(data["valor"])]),8, "expected 8 non-nulls: 5 given, 3 extrapolated")
        self.assertAlmostEqual(float(result["valor"][7]), 3.5, 2, "Expected 3.5, got %f" % result["valor"][7])

    def test_raise_not_enough_obs(self):
        data = DataFrame({
            "date": date_range(start=Timestamp(2000,1,1), periods=10, freq='D'),
            "valor": [0, 0.5, 1, 1.5, 2, NA, NA, NA, NA, NA]
        })

        # set index
        data.set_index("date", inplace=True)

        with self.assertRaises(ValueError):
            extrapolate_linear(
            data = data, column = "valor", 
            extrapolation_limit = 3, 
            train_length = 6)
        