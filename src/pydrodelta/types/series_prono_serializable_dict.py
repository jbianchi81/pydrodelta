from typing import TypedDict, List
from a5client.util_types import TVPserializable

class SeriesPronoSerializableDict(TypedDict):
    """
    Parameters:
    -----------
    series_id : int
    
    series_table : str
    
    pronosticos: List[TVP]
    """
    series_id : int
    series_table : str
    pronosticos: List[TVPserializable]
