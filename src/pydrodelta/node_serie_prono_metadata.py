# import dateutil.parser
from .descriptors.int_descriptor import IntDescriptor
from .descriptors.string_descriptor import StringDescriptor
from .descriptors.datetime_descriptor import DatetimeDescriptor
from datetime import datetime
from typing import List, Optional

class NodeSeriePronoMetadata:
    """Forecasted series metadata"""

    series_id = IntDescriptor()
    """Series identifier"""

    series_table = StringDescriptor()
    """One of series, series_areal, series_rast"""

    cal_id = IntDescriptor()
    """Procedure configuration identifier"""

    cor_id = IntDescriptor() 
    """Procedure run identifier"""

    forecast_date = DatetimeDescriptor() # dateutil.parser.isoparse(params["forecast_date"]) if "forecast_date" in params else None
    """Procedure execution date"""

    qualifier = StringDescriptor()
    """Forecast qualifier"""

    qualifiers : Optional[List[str]]
    """Forecast qualifiers"""

    forecast_timestart = DatetimeDescriptor()
    """When concatenating history of runs, lower bound of forecast_date """

    forecast_timeend = DatetimeDescriptor()
    """When concatenating history of runs, upper bound of forecast_date """

    def __init__(
        self,
        series_id : Optional[int] = None,
        cal_id : Optional[int] = None,
        cor_id : Optional[int] = None,
        forecast_date : Optional[str] = None,
        qualifier : Optional[str] = None,
        series_table : Optional[str] = "series",
        forecast_timestart : Optional[datetime] = None,
        forecast_timeend : Optional[datetime] = None,
        qualifiers : Optional[List[str]] = None
        ):
        """
        series_id : int = None

            Series identifier

        cal_id : int = None

            Procedure configuration identifier

        cor_id : int = None

            Procedure run identifier

        forecast_date : str = None

            Procedure execution date

        qualifier : str = None

            Forecast qualifier
        
        series_table :str = "series"
           One of series, series_areal, series_rast

        forecast_timestart : datetime = None
            When concatenating history of runs, lower bound of forecast_date 

        forecast_timeend : datetime = None
            When concatenating history of runs, upper bound of forecast_date 

        qualifiers : List[str] = None

            Forecast qualifiers
        

        """
        self.series_id = series_id
        self.cal_id = cal_id
        self.cor_id = cor_id
        self.forecast_date = forecast_date
        self.qualifier = qualifier
        self.series_table = series_table
        self.forecast_timestart = forecast_timestart
        self.forecast_timeend = forecast_timeend
        self.qualifiers = qualifiers
    def to_dict(self) -> dict:
        """Convert to dict"""
        return {
            "series_id": self.series_id,
            "series_table": self.series_table,
            "cal_id": self.cal_id,
            "cor_id": self.cor_id,
            "forecast_date": self.forecast_date,
            "qualifier": self.qualifier,
            "forecast_timestart": self.forecast_timestart,
            "forecast_timeend": self.forecast_timeend,
            "qualifiers": self.qualifiers
        }
