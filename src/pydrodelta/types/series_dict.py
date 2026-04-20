from typing import TypedDict, List
from a5client.util_types import TVP

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
