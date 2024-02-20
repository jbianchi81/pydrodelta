from typing import TypedDict, List
from .tvp import TVP

class SeriesDict(TypedDict):
    """
    Parameters:
    -----------
    series_id : int
    
    series_table : str
    
    observaciones: List[TVP]
    """
    series_id : int
    series_table : str
    observaciones: List[TVP]
