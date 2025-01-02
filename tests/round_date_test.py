from unittest import TestCase
from pydrodelta.util import roundDate
from datetime import datetime, timedelta
# import pytz 
from zoneinfo import ZoneInfo

class Test_RoundDate(TestCase):

    def test_input_date_is_round(self):
        date = datetime(2000,1,1,0,0,0,0,ZoneInfo('America/Buenos_Aires'))
        timeOffset = timedelta(days=0)
        timeInterval = timedelta(days=1)
        result = roundDate(date, timeInterval, timeOffset, "down")
        self.assertEqual(date.isoformat(), result.isoformat(), "expected: %s, got %s" % (date.isoformat(), result.isoformat()))

    def test_round_down(self):
        date = datetime(2000,1,1,12,0,0,0,ZoneInfo('America/Buenos_Aires'))
        timeOffset = timedelta(days=0)
        timeInterval = timedelta(days=1)
        expected_result = datetime(2000,1,1,0,0,0,0,ZoneInfo('America/Buenos_Aires'))
        result = roundDate(date, timeInterval, timeOffset, "down")
        self.assertEqual(expected_result.isoformat(), result.isoformat(), "expected: %s, got %s" % (date.isoformat(), result.isoformat()))

    def test_round_up(self):
        date = datetime(2000,1,1,12,0,0,0,ZoneInfo('America/Buenos_Aires'))
        timeOffset = timedelta(days=0)
        timeInterval = timedelta(days=1)
        expected_result = datetime(2000,1,2,0,0,0,0,ZoneInfo('America/Buenos_Aires'))
        result = roundDate(date, timeInterval, timeOffset, "up")
        self.assertEqual(expected_result.isoformat(), result.isoformat(), "expected: %s, got %s" % (date.isoformat(), result.isoformat()))
