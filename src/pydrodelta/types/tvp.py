from typing import TypedDict, Optional
from datetime import datetime

class TVP(TypedDict):
    """
    Parameters:
    -----------
    timestart : datetime
    
    valor : float

    series_id : int = None
    """
    timestart : datetime
    valor : float
    series_id : Optional[int]
