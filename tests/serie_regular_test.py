from unittest import TestCase
from pydrodelta.util import serieRegular
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz 
from pandas import DataFrame
# from zoneinfo import ZoneInfo

class Test_SerieRegular(TestCase):

    tz = pytz.timezone("America/Argentina/Buenos_Aires")

    def test_regular_serie(self):
        date = self.tz.localize(datetime(2000,1,1,0,0,0,0)) # ZoneInfo('America/Buenos_Aires'))
        timeOffset = relativedelta(days=0)
        timeInterval = relativedelta(days=1)

        data = DataFrame([
            {"timestart": date, "valor": 1.1},
            {"timestart": date + relativedelta(hours=23), "valor": 2.2},
            {"timestart": date + relativedelta(days=2,hours=1), "valor": 3.3},
            {"timestart": date  + relativedelta(days=2,hours=22), "valor": 4.4},
            {"timestart": date  + relativedelta(days=5,hours=1), "valor": 6.6}
        ]).set_index("timestart")
        result = serieRegular(
            data, 
            time_interval = timeInterval, 
            timestart = date, 
            timeend = date + relativedelta(days=6), 
            time_offset = timeOffset, 
            interpolate = True, 
            interpolation_limit = relativedelta(hours=26),
            tag_column = None, 
            extrapolate = False,
            agg_func = None,
            extrapolate_function = "linear",
            extrapolate_train_length = 5)
        assert len(result) == 7
        assert len(result.dropna()) == 7

