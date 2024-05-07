from typing import TypedDict, List
from .series_prono_dict import SeriesPronoDict
from datetime import datetime

class CorridaDict(TypedDict):
    """
    Parameters:
    -----------
    cal_id : int
    
    id : int

    forecast_date : datetime
    
    series: List[SeriesPronoDict]
    """
    cal_id : int
    id : int
    forecast_date : datetime
    series: List[SeriesPronoDict]
