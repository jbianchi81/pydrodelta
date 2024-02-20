from typing import TypedDict
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
    series_id : int = None
