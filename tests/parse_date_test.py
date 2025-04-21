from unittest import TestCase
from pydrodelta.util import tryParseAndLocalizeDate, createDatetimeSequence
from datetime import datetime
import pytz
from pandas import DataFrame
import logging
# from zoneinfo import ZoneInfo

class Test_ParseDate(TestCase):

    def test_parse_string(self):
        date = tryParseAndLocalizeDate("2000-01-01 00:00")
        self.assertEqual(date.year, 2000)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)
        self.assertEqual(date.hour, 0)
        self.assertEqual(date.minute, 0)
        self.assertEqual(date.second, 0)
        self.assertEqual(date.utcoffset().total_seconds() / 3600, -3)

    def test_monthly_sequence(self):
        tz = pytz.timezone("America/Argentina/Buenos_Aires")
        timestart = tz.localize(datetime(1900,1,1))
        timeend = tz.localize(datetime(2000,1,1)) 
        dts = createDatetimeSequence(
            timeInterval={"months":1},
            timestart = timestart, 
            timeend = timeend
        )
        for i,t in enumerate(dts):
            if i > 0:
                self.assertTrue(t.month != dts[i-1].month)

        df = DataFrame(index=dts)
        df["month"] = df.index.month
        for i, row in df.reset_index().iterrows():
            if i > 0 and row["month"] == df.iloc[i-1]["month"]:
                logging.error("Bad date: %s" % str(row["index"]))
        gb = df.groupby("month").size()
        self.assertEqual(len(gb),12)
        for count in gb.values:
            self.assertEqual(count,100)

    def test_yearly_sequence(self):
        tz = pytz.timezone("America/Argentina/Buenos_Aires")
        timestart = tz.localize(datetime(1900,1,1))
        timeend = tz.localize(datetime(2000,1,1)) 
        dts = createDatetimeSequence(
            timeInterval={"years":1},
            timestart = timestart, 
            timeend = timeend
        )
        for i,t in enumerate(dts):
            if i > 0:
                self.assertTrue(t.year != dts[i-1].year)

        df = DataFrame(index=dts)
        df["year"] = df.index.year
        for i, row in df.reset_index().iterrows():
            if i > 0 and row["year"] == df.iloc[i-1]["year"]:
                logging.error("Bad date: %s" % str(row["index"]))
        gb = df.groupby("year").size()
        self.assertEqual(len(gb),100)
        for count in gb.values:
            self.assertEqual(count,1)

    def test_daily_sequence(self):
        tz = pytz.timezone("America/Argentina/Buenos_Aires")
        timestart = tz.localize(datetime(1900,1,1))
        timeend = tz.localize(datetime(2000,1,1)) 
        dts = createDatetimeSequence(
            timeInterval={"days":1},
            timestart = timestart, 
            timeend = timeend
        )
        for i,t in enumerate(dts):
            if i > 0:
                self.assertTrue(t.day != dts[i-1].day)

        df = DataFrame(index=dts)
        df["day"] = df.index.day
        for i, row in df.reset_index().iterrows():
            if i > 0 and row["day"] == df.iloc[i-1]["day"]:
                logging.error("Bad date: %s" % str(row["index"]))
        gb = df.groupby("day").size()
        self.assertEqual(len(gb),31)
        for count in gb.values:
            self.assertTrue(count <= 100 * 12)

    def test_daily_sequence_with_offset(self):
        tz = pytz.timezone("America/Argentina/Buenos_Aires")
        timestart = tz.localize(datetime(1900,1,1))
        timeend = tz.localize(datetime(2000,1,1)) 
        offset = {"hours":12}
        dts = createDatetimeSequence(
            timeInterval={"days":1},
            timestart = timestart, 
            timeend = timeend,
            timeOffset = offset
        )
        for i,t in enumerate(dts):
            if i > 0:
                self.assertTrue(t.day != dts[i-1].day)

        df = DataFrame(index=dts)
        df["day"] = df.index.day
        for i, row in df.reset_index().iterrows():
            if i > 0:
                if row["day"] == df.iloc[i-1]["day"]:
                    logging.error("Bad date: %s" % str(row["index"]))
                self.assertTrue(row["day"] != df.iloc[i-1]["day"])
            self.assertEqual(df.index[i].hour, offset["hours"])
                
        gb = df.groupby("day").size()
        self.assertEqual(len(gb),31)
        for count in gb.values:
            self.assertTrue(count <= 100 * 12)
