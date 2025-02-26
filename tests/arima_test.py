from unittest import TestCase
from pydrodelta.arima import adjustSeriesArima
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pandas import DataFrame, date_range
from numpy import nan

class Test_ARIMA(TestCase):

    def test_arima(self):
        data = DataFrame({
            "timestart": date_range(start="2024-01-01", periods=8, freq="D"),
            "valor": [1,2,3,4,5,6,nan,nan],
            "valor_sim": [3,4,5,7,8,9,10,12]
        })
        data.set_index("timestart")
        arima_model, data_adj = adjustSeriesArima(data)

        self.assertEqual(len(data_adj) == len(data))
