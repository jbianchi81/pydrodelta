from typing import TypedDict, List
from .tvp import TVP

class SeriesPronoDict(TypedDict):
    """
    Parameters:
    -----------
    series_id : int
    
    series_table : str
    
    pronosticos: List[TVP]
    """
    series_id : int
    series_table : str
    pronosticos: List[TVP]
