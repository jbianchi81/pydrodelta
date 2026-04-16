from typing import TypedDict, Optional
from datetime import datetime

class TVPAllowNone(TypedDict):
    """
    Parameters:
    -----------
    timestart : datetime
    
    valor : float

    series_id : int = None
    """
    timestart : datetime
    valor : Optional[float]
    series_id : Optional[int]
